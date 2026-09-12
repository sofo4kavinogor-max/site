from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calc', methods=['GET', 'POST'])
def calc():
    result = None
    name = ''
    error = ''

    if request.method == 'POST':
        name = request.form.get('name', 'Воин').strip() or 'Воин'

        try:
            age = int(request.form.get('age', 25))
            weight = float(request.form.get('weight', 70))
            height = float(request.form.get('height', 175))
        except (ValueError, TypeError):
            error = 'Введи корректные числа'
            return render_template('calc.html', result=None, name=name, error=error)

        # Проверка границ
        if weight < 10:
            error = 'Вес не может быть меньше 10 кг'
        elif weight > 500:
            error = 'Вес не может быть больше 500 кг'
        elif height < 50:
            error = 'Рост не может быть меньше 50 см'
        elif height > 250:
            error = 'Рост не может быть больше 250 см'

        if error:
            return render_template('calc.html', result=None, name=name, error=error)

        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'keep')

        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        calories = round(bmr * 1.55)

        if goal == 'lose':
            calories -= 400
        elif goal == 'gain':
            calories += 400

        protein = round(weight * 1.8)
        fat = round(weight * 0.9)
        carbs = max(round((calories - protein * 4 - fat * 9) / 4), 0)

        result = {
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
        }

    return render_template('calc.html', result=result, name=name, error=error)


@app.route('/tariffs')
def tariffs():
    return render_template('tariffs.html')


@app.route('/plan/lite', methods=['GET', 'POST'])
def plan_lite():
    result = None
    name = ''

    if request.method == 'POST':
        name = request.form.get('name', 'Воин').strip() or 'Воин'

        try:
            age = int(request.form.get('age', 25))
            weight = float(request.form.get('weight', 70))
            height = float(request.form.get('height', 175))
        except (ValueError, TypeError):
            age, weight, height = 25, 70.0, 175.0

        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'keep')

        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        calories = round(bmr * 1.375)

        if goal == 'lose':
            calories -= 400
        elif goal == 'gain':
            calories += 400

        protein = round(weight * 1.8)
        fat = round(weight * 0.9)
        carbs = max(round((calories - protein * 4 - fat * 9) / 4), 0)

        result = {
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
        }

    return render_template('plan_lite.html', result=result, name=name)


@app.route('/plan/max', methods=['GET', 'POST'])
def plan_max():
    result = None
    name = ''

    if request.method == 'POST':
        name = request.form.get('name', 'Воин').strip() or 'Воин'

        try:
            age = int(request.form.get('age', 25))
            weight = float(request.form.get('weight', 70))
            height = float(request.form.get('height', 175))
        except (ValueError, TypeError):
            age, weight, height = 25, 70.0, 175.0

        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'keep')

        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        calories = round(bmr * 1.55)

        if goal == 'lose':
            calories -= 400
        elif goal == 'gain':
            calories += 400

        protein = round(weight * 1.8)
        fat = round(weight * 0.9)
        carbs = max(round((calories - protein * 4 - fat * 9) / 4), 0)

        result = {
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
        }

    return render_template('plan_max.html', result=result, name=name)


@app.route('/plan/promaxing', methods=['GET', 'POST'])
def plan_promaxing():
    result = None
    name = ''

    if request.method == 'POST':
        name = request.form.get('name', 'Воин').strip() or 'Воин'

        try:
            age = int(request.form.get('age', 25))
            weight = float(request.form.get('weight', 70))
            height = float(request.form.get('height', 175))
        except (ValueError, TypeError):
            age, weight, height = 25, 70.0, 175.0

        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'keep')
        experience = request.form.get('experience', 'mid')

        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        if experience == 'new':
            activity = 1.55
        elif experience == 'mid':
            activity = 1.725
        else:
            activity = 1.9

        calories = round(bmr * activity)

        if goal == 'lose':
            calories -= 400
        elif goal == 'gain':
            calories += 400

        protein = round(weight * 2.0)
        fat = round(weight * 0.9)
        carbs = max(round((calories - protein * 4 - fat * 9) / 4), 0)

        result = {
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
        }

    return render_template('plan_promaxing.html', result=result, name=name)


@app.route('/api/nearby', methods=['POST'])
def api_nearby():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    if not lat or not lon:
        return {'error': 'Нет координат'}, 400

    YANDEX_KEY = '7b4850b8-b55a-4b0e-baad-45795b62aa90'

    categories = [
        ('gym', 'спортзал'),
        ('sportpit', 'спортивное питание'),
        ('cafe', 'кафе'),
    ]

    places = []

    for cat_key, query in categories:
        try:
            r = requests.get(
                'https://search-maps.yandex.ru/v1/',
                params={
                    'apikey': YANDEX_KEY,
                    'text': query,
                    'type': 'biz',
                    'll': f'{lon},{lat}',
                    'spn': '0.09,0.09',
                    'rspn': 1,
                    'results': 15,
                    'lang': 'ru_RU',
                },
                timeout=15
            )
            data_y = r.json()
        except Exception:
            continue

        for feature in data_y.get('features', []):
            props = feature.get('properties', {})
            company = props.get('CompanyMetaData', {})
            place_name = company.get('name', 'Без названия')
            address = company.get('address', '')

            coords = feature.get('geometry', {}).get('coordinates', [None, None])
            lon_p, lat_p = coords[0], coords[1]

            if cat_key == 'gym':
                category = 'Спортзал'
            elif cat_key == 'sportpit':
                category = 'Спортпит'
            else:
                category = 'Кафе'

            places.append({
                'name': place_name,
                'category': category,
                'lat': lat_p,
                'lon': lon_p,
                'address': address,
            })

    return {'places': places}


if __name__ == '__main__':
    app.run(debug=True)