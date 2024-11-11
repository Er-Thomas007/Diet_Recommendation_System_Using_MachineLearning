import streamlit as st
import csv

# Define the VfcDietRecommendation class
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

        if self.activity_level == "sedentary":
            bmr *= 1.2
        elif self.activity_level == "lightly_active":
            bmr *= 1.375
        elif self.activity_level == "moderately_active":
            bmr *= 1.55
        elif self.activity_level == "very_active":
            bmr *= 1.725
        elif self.activity_level == "extra_active":
            bmr *= 1.9

        if goal == "weight_loss":
            return bmr * 0.8
        elif goal == "weight_gain":
            return bmr * 1.2

    def load_food_items(self, csv_file):
        food_items = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                food_items.append(row)
        return food_items

    def select_meal(self, food_items, target_calories):
        closest_meal = None
        closest_distance = float('inf')

        for meal in food_items:
            calorie_count = int(meal['Calories'])
            distance = abs(calorie_count - target_calories)

            if distance < closest_distance:
                closest_meal = meal
                closest_distance = distance

        return closest_meal

    def recommend_diet(self, goal, breakfast_csv, lunch_csv, dinner_csv):
        total_calories = self.calculate_calories(goal)

        breakfast_items = self.load_food_items(breakfast_csv)
        lunch_items = self.load_food_items(lunch_csv)
        dinner_items = self.load_food_items(dinner_csv)

        breakfast_calories = total_calories * 0.3  # 30% of total calories
        lunch_calories = total_calories * 0.4  # 40% of total calories
        dinner_calories = total_calories * 0.3  # 30% of total calories

        recommended_diet = {
            "Breakfast": self.select_meal(breakfast_items, breakfast_calories),
            "Lunch": self.select_meal(lunch_items, lunch_calories),
            "Dinner": self.select_meal(dinner_items, dinner_calories)
        }

        return recommended_diet

# Function to display recommended diet
def display_diet(recommended_diet):
    st.subheader("Recommended Diet")
    st.write("Breakfast:")
    st.write(recommended_diet["Breakfast"])
    st.write("Lunch:")
    st.write(recommended_diet["Lunch"])
    st.write("Dinner:")
    st.write(recommended_diet["Dinner"])





# Sidebar inputs
st.sidebar.title("User Information")
age = st.sidebar.slider("Age", min_value=0, max_value=120, value=20)
height = st.sidebar.slider("Height (cm)", min_value=0.0, max_value=300.0, value=167.64)
weight = st.sidebar.slider("Weight (kg)", min_value=0.0, max_value=500.0, value=54.0)
activity_level = st.sidebar.selectbox("Activity Level", ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"])
body_type = st.sidebar.selectbox("Body Type", ["endomorphic", "ectomorphic", "mesomorphic"])
goal = st.sidebar.selectbox("Goal", ["weight_loss", "weight_gain"])

# Display user inputs
st.sidebar.subheader("User Details")
st.sidebar.write(f"Age: {age}")
st.sidebar.write(f"Height: {height} cm")
st.sidebar.write(f"Weight: {weight} kg")
st.sidebar.write("Activity Level:", activity_level)
st.sidebar.write("Body Type:", body_type)
st.sidebar.write("Goal:", goal)

# Button to recommend diet
if st.sidebar.button("Recommend Diet"):
    # Instantiate the VfcDietRecommendation class
    user = VfcDietRecommendation(age, height, weight, activity_level, body_type)
    # Call the recommend_diet method with correct file paths
    recommended_diet = user.recommend_diet(goal, "Data_Set/Breakfast_data.csv", "Data_Set/Lunch_data.csv", "Data_Set/Dinner_data.csv")
    # Display the recommended diet
    display_diet(recommended_diet)
