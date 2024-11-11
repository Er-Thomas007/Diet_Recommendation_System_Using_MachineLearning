import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
import joblib
import csv

class VfcDietRecommendation:
    def __init__(self, age, height, weight, activity_level, body_type):
        self.age = age
        self.height = height
        self.weight = weight
        self.activity_level = activity_level
        self.body_type = body_type
        self.bmr = self.calculate_bmr()

    def calculate_bmr(self):
        if self.body_type == "endomorphic":
            return (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        elif self.body_type == "ectomorphic":
            return (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        elif self.body_type == "mesomorphic":
            return (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 100

    def calculate_calories(self, goal):
        bmr = self.bmr

        activity_levels = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extra_active": 1.9
        }

        activity_multiplier = activity_levels.get(self.activity_level, 1.0)

        bmr *= activity_multiplier

        if goal == "weight_loss":
            return bmr * 0.8
        elif goal == "weight_gain":
            return bmr * 1.2

    @staticmethod
    def load_food_items(csv_file):
        food_items = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                food_items.append(row)
        return food_items

    @staticmethod
    def select_meal(food_items, target_calories):
        closest_meal = min(food_items, key=lambda x: abs(int(x['Calories']) - target_calories))
        return closest_meal

    def recommend_diet(self, goal, breakfast_csv, lunch_csv, dinner_csv):
        total_calories = self.calculate_calories(goal)

        if goal == "weight_loss":
            breakfast_percentage = 0.3  # 30% of total calories
            lunch_percentage = 0.4  # 40% of total calories
            dinner_percentage = 0.3  # 30% of total calories
        elif goal == "weight_gain":
            breakfast_percentage = 0.25  # 25% of total calories
            lunch_percentage = 0.35  # 35% of total calories
            dinner_percentage = 0.4  # 40% of total calories

        breakfast_calories = total_calories * breakfast_percentage
        lunch_calories = total_calories * lunch_percentage
        dinner_calories = total_calories * dinner_percentage

        breakfast_items = self.load_food_items(breakfast_csv)
        lunch_items = self.load_food_items(lunch_csv)
        dinner_items = self.load_food_items(dinner_csv)

        recommended_diet = {
            "Breakfast": {"Items": [], "Total Calories": 0},
            "Lunch": {"Items": [], "Total Calories": 0},
            "Dinner": {"Items": [], "Total Calories": 0},
        }

        recommended_diet["Breakfast"]["Items"].append(self.select_meal(breakfast_items, breakfast_calories))
        recommended_diet["Lunch"]["Items"].append(self.select_meal(lunch_items, lunch_calories))
        recommended_diet["Dinner"]["Items"].append(self.select_meal(dinner_items, dinner_calories))

        for meal, items in recommended_diet.items():
            total_calories = sum(int(item["Calories"]) for item in items["Items"] if item)
            recommended_diet[meal]["Total Calories"] = total_calories

        return recommended_diet

class DietRecommendationSystem:
    def __init__(self, user):
        self.user = user
        self.breakfast_items = pd.read_csv("Data_Set/Breakfast_data.csv")
        self.lunch_items = pd.read_csv("Data_Set/Lunch_data.csv")
        self.dinner_items = pd.read_csv("Data_Set/Dinner_data.csv")

    @staticmethod
    def knn_recommendation(meal_items, target_calories, k=5):
        X = meal_items[['Calories']].values
        nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(X)
        distances, indices = nbrs.kneighbors([[target_calories]])
        recommended_items = meal_items.iloc[indices[0]]
        return recommended_items

    @staticmethod
    def kmeans_recommendation(meal_items, target_calories, k=3):
        X = meal_items[['Calories']].values
        kmeans = KMeans(n_clusters=k, random_state=42).fit(X)
        cluster_centers = kmeans.cluster_centers_
        distances = [abs(calories - target_calories) for calories in cluster_centers[:, 0]]
        closest_cluster_index = distances.index(min(distances))
        cluster_items = meal_items[kmeans.labels_ == closest_cluster_index]
        return cluster_items

def main():
    st.title("Diet Recommendation System")

    st.sidebar.header("User Information")
    age = st.sidebar.number_input("Age", min_value=1, max_value=150, step=1)
    height = st.sidebar.number_input("Height (cm)", min_value=1, max_value=300, step=1)
    weight = st.sidebar.number_input("Weight (kg)", min_value=1, max_value=500, step=1)
    activity_level = st.sidebar.selectbox("Activity Level", ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"])
    body_type = st.sidebar.selectbox("Body Type", ["endomorphic", "ectomorphic", "mesomorphic"])
    goal = st.sidebar.selectbox("Goal", ["weight_loss", "weight_gain"])

    user = VfcDietRecommendation(age, height, weight, activity_level, body_type)
    diet_system = DietRecommendationSystem(user)

    if st.button("Recommend Diet"):
        st.write(f"User Information: Age: {age}, Height: {height} cm, Weight: {weight} kg, Activity Level: {activity_level}, Body Type: {body_type}")
        st.write(f"Goal: {goal.capitalize()}")

        # Load the K-NN model
        knn_model = joblib.load("knn_model.pkl")

        # Calculate total calories for each meal
        total_calories = user.calculate_calories(goal)
        breakfast_calories = total_calories * 0.3
        lunch_calories = total_calories * 0.4
        dinner_calories = total_calories * 0.3

        # Make recommendations using K-NN model
        recommended_breakfast = diet_system.knn_recommendation(diet_system.breakfast_items, breakfast_calories)
        recommended_lunch = diet_system.knn_recommendation(diet_system.lunch_items, lunch_calories)
        recommended_dinner = diet_system.knn_recommendation(diet_system.dinner_items, dinner_calories)

        st.subheader("Recommended Diet (K-NN)")
        st.write("Breakfast:")
        st.write(recommended_breakfast)
        st.write("Lunch:")
        st.write(recommended_lunch)
        st.write("Dinner:")
        st.write(recommended_dinner)

if __name__ == "__main__":
    main()
