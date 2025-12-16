from django.core.management.base import BaseCommand
from django.contrib.auth.models import User as AuthUser
from api.models import Category, GeoPosition, Clinic, User, SupportRequest, Review


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных...')

        # Создание категорий
        self.stdout.write('Создание категорий...')
        categories_data = [
            'Кардиолог',
            'Невролог',
            'Педиатр',
            'Терапевт',
            'Хирург',
            'Офтальмолог',
            'Стоматолог',
            'Дерматолог',
        ]
        categories = {}
        for cat_title in categories_data:
            category, created = Category.objects.get_or_create(title=cat_title)
            categories[cat_title] = category
            if created:
                self.stdout.write(f'  [OK] Создана категория: {cat_title}')

        # Создание геопозиций
        self.stdout.write('Создание геопозиций...')
        geopositions_data = [
            'Алматы',
            'Астана',
            'Шымкент',
            'Караганда',
            'Актобе',
        ]
        geopositions = {}
        for geo_title in geopositions_data:
            geoposition, created = GeoPosition.objects.get_or_create(title=geo_title)
            geopositions[geo_title] = geoposition
            if created:
                self.stdout.write(f'  [OK] Создана геопозиция: {geo_title}')

        # Создание клиник
        self.stdout.write('Создание клиник...')
        clinics_data = [
            {
                'title': 'Медицинский центр "Здоровье"',
                'address': 'ул. Абая, 150, Алматы',
                'phone': '+7 (727) 123-45-67',
                'email': 'info@zdorovie.kz',
                'work_time': 'Пн-Пт: 9:00-18:00, Сб: 9:00-14:00',
            },
            {
                'title': 'Клиника "Медикал Плюс"',
                'address': 'пр. Достык, 240, Алматы',
                'phone': '+7 (727) 234-56-78',
                'email': 'info@medicalplus.kz',
                'work_time': 'Пн-Вс: 8:00-20:00',
            },
            {
                'title': 'Больница скорой помощи',
                'address': 'ул. Сатпаева, 90, Алматы',
                'phone': '+7 (727) 345-67-89',
                'email': 'info@bsmp.kz',
                'work_time': 'Круглосуточно',
            },
            {
                'title': 'Медицинский центр "Астана"',
                'address': 'пр. Кабанбай батыра, 15, Астана',
                'phone': '+7 (7172) 123-45-67',
                'email': 'info@astana-med.kz',
                'work_time': 'Пн-Пт: 8:00-19:00, Сб: 9:00-15:00',
            },
            {
                'title': 'Клиника "Дентал"',
                'address': 'ул. Байтурсынова, 50, Шымкент',
                'phone': '+7 (7252) 234-56-78',
                'email': 'info@dental.kz',
                'work_time': 'Пн-Сб: 9:00-18:00',
            },
        ]
        clinics = {}
        for clinic_data in clinics_data:
            clinic, created = Clinic.objects.get_or_create(
                title=clinic_data['title'],
                defaults=clinic_data
            )
            clinics[clinic_data['title']] = clinic
            if created:
                self.stdout.write(f'  [OK] Создана клиника: {clinic_data["title"]}')

        # Создание пользователей (пациентов)
        self.stdout.write('Создание пользователей (пациентов)...')
        patients_data = [
            {'telegram_id': 1001, 'phone_number': '+77001234567', 'geo_position': 'Алматы'},
            {'telegram_id': 1002, 'phone_number': '+77002345678', 'geo_position': 'Астана'},
            {'telegram_id': 1003, 'phone_number': '+77003456789', 'geo_position': 'Шымкент'},
            {'telegram_id': 1004, 'phone_number': '+77004567890', 'geo_position': 'Алматы'},
            {'telegram_id': 1005, 'phone_number': '+77005678901', 'geo_position': 'Караганда'},
        ]
        patients = {}
        for patient_data in patients_data:
            geo = geopositions.get(patient_data['geo_position'])
            patient, created = User.objects.get_or_create(
                telegram_id=patient_data['telegram_id'],
                defaults={
                    'phone_number': patient_data['phone_number'],
                    'geo_position': geo,
                    'patient': True,
                    'doctor': False,
                }
            )
            patients[patient_data['telegram_id']] = patient
            if created:
                self.stdout.write(f'  [OK] Создан пациент: {patient_data["telegram_id"]}')

        # Создание врачей
        self.stdout.write('Создание врачей...')
        doctors_data = [
            {
                'telegram_id': 2001,
                'category': 'Кардиолог',
                'clinic': 'Медицинский центр "Здоровье"',
                'geo_position': 'Алматы',
                'phone_number': '+77011111111',
                'detail': 'Опытный кардиолог с 15-летним стажем. Специализация: лечение ишемической болезни сердца.',
            },
            {
                'telegram_id': 2002,
                'category': 'Невролог',
                'clinic': 'Клиника "Медикал Плюс"',
                'geo_position': 'Алматы',
                'phone_number': '+77012222222',
                'detail': 'Врач-невролог высшей категории. Лечение заболеваний нервной системы.',
            },
            {
                'telegram_id': 2003,
                'category': 'Педиатр',
                'clinic': 'Медицинский центр "Здоровье"',
                'geo_position': 'Алматы',
                'phone_number': '+77013333333',
                'detail': 'Детский врач с большим опытом работы. Специализация: лечение детей от 0 до 18 лет.',
            },
            {
                'telegram_id': 2004,
                'category': 'Терапевт',
                'clinic': 'Медицинский центр "Астана"',
                'geo_position': 'Астана',
                'phone_number': '+77014444444',
                'detail': 'Врач-терапевт общей практики. Консультации и лечение общих заболеваний.',
            },
            {
                'telegram_id': 2005,
                'category': 'Хирург',
                'clinic': 'Больница скорой помощи',
                'geo_position': 'Алматы',
                'phone_number': '+77015555555',
                'detail': 'Хирург высшей категории. Проведение операций различной сложности.',
            },
            {
                'telegram_id': 2006,
                'category': 'Офтальмолог',
                'clinic': 'Клиника "Медикал Плюс"',
                'geo_position': 'Алматы',
                'phone_number': '+77016666666',
                'detail': 'Врач-офтальмолог. Диагностика и лечение заболеваний глаз.',
            },
            {
                'telegram_id': 2007,
                'category': 'Стоматолог',
                'clinic': 'Клиника "Дентал"',
                'geo_position': 'Шымкент',
                'phone_number': '+77017777777',
                'detail': 'Стоматолог-терапевт. Лечение кариеса, пломбирование, отбеливание.',
            },
            {
                'telegram_id': 2008,
                'category': 'Дерматолог',
                'clinic': 'Медицинский центр "Здоровье"',
                'geo_position': 'Алматы',
                'phone_number': '+77018888888',
                'detail': 'Врач-дерматолог. Лечение кожных заболеваний, косметология.',
            },
        ]
        doctors = {}
        for doctor_data in doctors_data:
            category = categories.get(doctor_data['category'])
            clinic = clinics.get(doctor_data['clinic'])
            geo = geopositions.get(doctor_data['geo_position'])
            doctor, created = User.objects.get_or_create(
                telegram_id=doctor_data['telegram_id'],
                defaults={
                    'category': category,
                    'clinic': clinic,
                    'geo_position': geo,
                    'phone_number': doctor_data['phone_number'],
                    'detail': doctor_data['detail'],
                    'patient': False,
                    'doctor': True,
                }
            )
            doctors[doctor_data['telegram_id']] = doctor
            if created:
                self.stdout.write(f'  [OK] Создан врач: {doctor_data["category"]} (ID: {doctor_data["telegram_id"]})')

        # Создание отзывов
        self.stdout.write('Создание отзывов...')
        reviews_data = [
            {'patient': 1001, 'doctor': 2001, 'rating': 5, 'detail': 'Отличный врач! Очень внимательный и профессиональный. Помог решить проблему с сердцем.'},
            {'patient': 1002, 'doctor': 2001, 'rating': 4, 'detail': 'Хороший специалист, но пришлось долго ждать приема.'},
            {'patient': 1003, 'doctor': 2001, 'rating': 5, 'detail': 'Рекомендую! Очень доволен результатом лечения.'},
            {'patient': 1001, 'doctor': 2002, 'rating': 5, 'detail': 'Превосходный невролог. Детально объяснил диагноз и назначил эффективное лечение.'},
            {'patient': 1004, 'doctor': 2002, 'rating': 4, 'detail': 'Хороший врач, но цены немного завышены.'},
            {'patient': 1002, 'doctor': 2003, 'rating': 5, 'detail': 'Замечательный педиатр! Ребенок не боится, очень добрый врач.'},
            {'patient': 1005, 'doctor': 2003, 'rating': 5, 'detail': 'Лучший детский врач в городе. Всегда помогает быстро.'},
            {'patient': 1003, 'doctor': 2004, 'rating': 4, 'detail': 'Нормальный терапевт, все по делу.'},
            {'patient': 1001, 'doctor': 2005, 'rating': 5, 'detail': 'Отличный хирург! Операция прошла успешно, быстро восстановился.'},
            {'patient': 1004, 'doctor': 2005, 'rating': 3, 'detail': 'Операция прошла нормально, но послеоперационный уход мог быть лучше.'},
            {'patient': 1002, 'doctor': 2006, 'rating': 5, 'detail': 'Очень хороший офтальмолог. Провел полное обследование, все объяснил.'},
            {'patient': 1005, 'doctor': 2007, 'rating': 4, 'detail': 'Хороший стоматолог, но немного болезненно.'},
            {'patient': 1003, 'doctor': 2007, 'rating': 5, 'detail': 'Отличный стоматолог! Безболезненно и качественно.'},
            {'patient': 1001, 'doctor': 2008, 'rating': 4, 'detail': 'Хороший дерматолог, помог с проблемой кожи.'},
            {'patient': 1004, 'doctor': 2008, 'rating': 5, 'detail': 'Превосходный специалист! Результат превзошел ожидания.'},
        ]
        for review_data in reviews_data:
            patient = patients.get(review_data['patient'])
            doctor = doctors.get(review_data['doctor'])
            if patient and doctor:
                review, created = Review.objects.get_or_create(
                    user=patient,
                    doctor=doctor,
                    defaults={
                        'rating': review_data['rating'],
                        'detail': review_data['detail'],
                    }
                )
                if created:
                    self.stdout.write(f'  [OK] Создан отзыв: пациент {review_data["patient"]} -> врач {review_data["doctor"]} (оценка: {review_data["rating"]})')

        # Создание запросов в поддержку
        self.stdout.write('Создание запросов в поддержку...')
        support_requests_data = [
            {'patient': 1001, 'detail': 'Не могу зарегистрироваться в системе'},
            {'patient': 1002, 'detail': 'Как оставить отзыв о враче?'},
            {'patient': 1003, 'detail': 'Проблема с поиском клиники'},
            {'patient': 1004, 'detail': 'Хочу изменить свой профиль'},
        ]
        for req_data in support_requests_data:
            patient = patients.get(req_data['patient'])
            if patient:
                request, created = SupportRequest.objects.get_or_create(
                    user=patient,
                    detail=req_data['detail'],
                )
                if created:
                    self.stdout.write(f'  [OK] Создан запрос в поддержку от пользователя {req_data["patient"]}')

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] База данных успешно заполнена!'))
        self.stdout.write(f'\nСтатистика:')
        self.stdout.write(f'  - Категорий: {Category.objects.count()}')
        self.stdout.write(f'  - Геопозиций: {GeoPosition.objects.count()}')
        self.stdout.write(f'  - Клиник: {Clinic.objects.count()}')
        self.stdout.write(f'  - Пользователей: {User.objects.count()} (пациентов: {User.objects.filter(patient=True).count()}, врачей: {User.objects.filter(doctor=True).count()})')
        self.stdout.write(f'  - Отзывов: {Review.objects.count()}')
        self.stdout.write(f'  - Запросов в поддержку: {SupportRequest.objects.count()}')

