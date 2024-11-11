from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load datasets
breakfast_df = pd.read_csv('Data_set/Breakfast.csv')
lunch_df = pd.read_csv('Data_set/Lunch.csv')
dinner_df = pd.read_csv('Data_set/Dinner.csv')

def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender == "female":
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def calculate_tdee(bmr, activity_level):
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)

def calculate_caloric_needs(age, height, weight, activity_level, gender, goal):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    if goal == "weight_loss":
        total_calories = tdee * 0.8
    elif goal == "weight_gain":
        total_calories = tdee + 500
    else:  # For maintenance
        total_calories = tdee
    
    return bmr, tdee, total_calories

def recommend_meals(age, height, weight, activity_level, gender, goal, veg_non_veg_pref, junk_food_pref):
    bmr, tdee, total_calories = calculate_caloric_needs(age, height, weight, activity_level, gender, goal)
    
    proportions = {
        'normal': (0.30, 0.40, 0.30),
        'weight_loss': (0.30, 0.40, 0.30),
        'weight_gain': (0.25, 0.35, 0.40)
    }
    proportion = proportions.get(goal, (0.30, 0.40, 0.30))
    breakfast_calories = total_calories * proportion[0]
    lunch_calories = total_calories * proportion[1]
    dinner_calories = total_calories * proportion[2]

    def get_recommendations(df, veg_non_veg_pref, junk_food_pref):
        if veg_non_veg_pref == 'both' and junk_food_pref == 'both':
            return df
        elif veg_non_veg_pref == 'both':
            return df[df['Junk Food'] == junk_food_pref]
        elif junk_food_pref == 'both':
            return df[df['VegNovVeg'] == veg_non_veg_pref]
        else:
            return df[(df['VegNovVeg'] == veg_non_veg_pref) & (df['Junk Food'] == junk_food_pref)]

    def select_best_items(df, target_calories):
        df_shuffled = df.sample(frac=1).reset_index(drop=True)
        selected_items = []
        total_calories = 0
        for _, row in df_shuffled.iterrows():
            if total_calories + row['Calories'] <= target_calories:
                selected_items.append(row)
                total_calories += row['Calories']
            if total_calories >= target_calories:
                break
        return selected_items, total_calories

    daily_recommendations = []
    for meal_df, meal_type, target_calories in zip(
            [breakfast_df, lunch_df, dinner_df],
            ['Breakfast', 'Lunch', 'Dinner'],
            [breakfast_calories, lunch_calories, dinner_calories]):
        
        filtered_df = get_recommendations(meal_df, veg_non_veg_pref, junk_food_pref)
        selected_items, meal_total_calories = select_best_items(filtered_df, target_calories)
        
        for item in selected_items:
            daily_recommendations.append({
                'Meal': meal_type,
                'Food Item': item['Food_items'],
                'Calories': item['Calories'],
                'Fats': item['Fats'],
                'Proteins': item['Proteins'],
                'Iron': item['Iron'],
                'Calcium': item['Calcium'],
                'Sodium': item['Sodium'],
                'Potassium': item['Potassium'],
                'Carbohydrates': item['Carbohydrates'],
                'Fibre': item['Fibre'],
                'VitaminD': item['VitaminD'],
                'Sugars': item['Sugars']
            })

    return daily_recommendations, bmr, tdee, total_calories

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.form
    age = int(data.get('age'))
    height = float(data.get('height'))
    weight = float(data.get('weight'))
    activity_level = data.get('activity_level')
    gender = data.get('gender')  # 'male' or 'female'
    goal = data.get('goal')
    veg_non_veg_pref = data.get('veg_non_veg_pref')  # Can be 'both', 'vegetarian', or 'non_vegetarian'
    junk_food_pref = data.get('junk_food_pref')  # Can be 'both', 'yes', or 'no'

    daily_recommendations, bmr, tdee, total_calories = recommend_meals(
        age, height, weight, activity_level, gender, goal, veg_non_veg_pref, junk_food_pref
    )

    return render_template('recommendations.html',
                           recommendations=daily_recommendations,
                           total_calories=total_calories,
                           bmr=bmr,
                           tdee=tdee,
                           goal=goal)

@app.route('/about')
def about_us():
    return render_template('about_us.html')

if __name__ == '__main__':
    app.run(debug=True)
