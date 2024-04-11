import re
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class FoodRecommendations:
    def __init__(self, dataset_path):
        print("Reading data from {}".format(dataset_path))
        data = pd.read_csv(dataset_path)

        print("Processing dataset")
        self.extracted_data = data[['RecipeId', 'Name', 'CookTime', 'PrepTime', 'TotalTime', 'RecipeIngredientParts',
                               'Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                               'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent',
                               'RecipeInstructions']]

        # Create a pipeline for data preprocessing and model training
        self.scaler = StandardScaler()
        self.neigh = NearestNeighbors(metric='cosine', algorithm='brute')
        self.pipeline = Pipeline([('std_scaler', self.scaler),
                             ('NN', self.neigh)])

        # Fit the pipeline on the extracted data
        self.pipeline.fit(self.extracted_data.iloc[:, 6:15].to_numpy())

        # Define the feature names
        self.feature_names = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                              'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
        print("Successfully loaded and encoded dataset.")

    def _convert_iso8601_to_minutes(self, iso8601_duration):
        # Regular expression to extract hours (H) and minutes (M) from an ISO 8601 duration string
        pattern = re.compile('PT(?:(\d+)H)?(?:(\d+)M)?')
        match = pattern.match(iso8601_duration)
        if not match:
            return 0  # Return 0 minutes if the string does not match the expected format

        hours, minutes = match.groups(default="0")
        total_minutes = int(hours) * 60 + int(minutes)
        return total_minutes

    def _preprocess_user_preferences(self, user_preferences):
        user_features = [user_preferences.get(feature, 0) for feature in self.feature_names]
        user_features_scaled = self.scaler.transform([user_features])
        return user_features_scaled

    def _get_recommendations(self, user_preferences, allergy_keywords, max_total_time=None, n=10):
        user_features_scaled = self._preprocess_user_preferences(user_preferences)
        _, neighbor_indices = self.pipeline['NN'].kneighbors(user_features_scaled,
                                                        n_neighbors=n * 2)  # Retrieve more neighbors
        recommended_recipes = self.extracted_data.iloc[neighbor_indices[0]]

        # Convert TotalTime from ISO 8601 format to minutes and filter based on max_total_time
        if max_total_time is not None:
            recommended_recipes['TotalTimeMinutes'] = recommended_recipes['TotalTime'].apply(
                self._convert_iso8601_to_minutes)
            recommended_recipes = recommended_recipes[recommended_recipes['TotalTimeMinutes'] <= max_total_time]

        # Filter out recipes containing the allergy keywords
        if allergy_keywords:
            for keyword in allergy_keywords:
                recommended_recipes = recommended_recipes[
                    ~recommended_recipes['RecipeIngredientParts'].str.contains(keyword, case=False)]

        return recommended_recipes.head(n)

    def get_recommendations(self, user_preferences, allergy_keywords=None, max_total_time=None, n=10):
        if allergy_keywords is None:
            allergy_keywords = []
        else:
            allergy_keywords = [keyword.strip() for keyword in allergy_keywords.split(',')]

        recommendations = self._get_recommendations(user_preferences, allergy_keywords, max_total_time, n)

        columns_to_print = ['Name']
        if 'RecipeCategory' in recommendations.columns:
            columns_to_print.append('RecipeCategory')
        if 'CookTime' in recommendations.columns:
            columns_to_print.append('CookTime')
        if 'PrepTime' in recommendations.columns:
            columns_to_print.append('PrepTime')
        if 'TotalTime' in recommendations.columns:
            columns_to_print.append('TotalTime')
        columns_to_print.append("RecipeId")

        recommended_recipes = []
        for idx, recipe in recommendations[columns_to_print].iterrows():
            recipe_info = {column: recipe[column] for column in columns_to_print}
            recommended_recipes.append(recipe_info)

        return recommended_recipes
