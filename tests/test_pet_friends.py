from api import PetFriends
from settings import valid_email, valid_password,unvalid_email, unvalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result

def test_get_api_key_for_unvalid_user(email=unvalid_email, password=valid_password):
    """ Проверяем что запрос api ключа с неверныйм почтовым адресом  возвращает статус равный 403 """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403

def test_get_api_key_for_unvalid_password(email=valid_email, password=unvalid_password):
    """ Проверяем что запрос api ключа  с неверным  паролем возвращает статус  равный 403 """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_unsuccessful_set_no_self_pet_photo(pet_photo='images/cat1.jpg'):
    """Проверяем невозможность добавления фото чужому питомцу"""

    # Получаем ключ auth_key и список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, pets = pf.get_list_of_pets(auth_key, "")
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

    photo = os.path.join(os.path.dirname(__file__), pet_photo)
    petid = pets['pets'][0]['id']

    status, result = pf.set_pet_photo(auth_key, petid, photo )
    assert status == 500
    # assert result['pet_photo'] != 'images/cat1.jpg'

def test_add_new_pet_with_valid_data(name='Пират', animal_type='кошак',
                                     age='пять', pet_photo='images/img003.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_add_new_pet_with_unvalid_data(name='', animal_type='кот',
                                     age='1', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с некорректными данными : отсутвует имя питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status != 200



def test_successful_delete_self_pet():
    """Проверяем возможность удаления своего питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_unsuccessful_delete_not_self_pet():
    """Проверяем невозможность удаления чужого питомца (баг: Можно удалить чужого питомца)"""

    # Получаем ключ auth_key и запрашиваем список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, pets = pf.get_list_of_pets(auth_key, "")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список  питомцев
    _, result = pf.get_list_of_pets(auth_key, "")

    if pet_id  in result.values() :
        assert pet_id in result.values()
    else:

        raise Exception("Delete is no my pets")


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")



def test_unsuccessful_update_self_pet_info_unvalid_age(name='Мурзик', animal_type='Котэ', age='пять'):
    """Проверяем невозможность обновления информации о питомце с добавлением не числового возраста питомца"""
    """баг : в поле возраст можно послать строку вместо числа """

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status != 200
        assert result['age'] != age
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_unsuccessful_update_not_self_pet_info(name='John Doe', animal_type='Животное', age=9999999):
    """Проверяем невозможность обновления информации о чужом питомце баг : можно изменить данные чужого питомца"""

    # Получаем ключ auth_key и список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, pets = pf.get_list_of_pets(auth_key, "")

    status, result = pf.update_pet_info(auth_key, pets['pets'][0]['id'], name, animal_type, age)

    if  result['name'] != name:
        assert status != 200
    else:
        raise Exception("Update info no my pets")

def test_add_new_pet_with_valid_data_without_foto(name='Матроскин', animal_type='кошка',
                                     age='0'):
    """Проверяем что можно добавить питомца с корректными данными без фото"""


    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] == ''

def test_successful_set_pet_photo(name='Пушок', animal_type='Кошак',
                                     age='1', pet_photo='images/cat1.jpg'):
    """Проверяем возможность добавления фото питомца"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Создаем питомца без фото и сохраняем его id
    _, result = pf.create_pet_simple(auth_key, name, animal_type,age)
    petid = result['id']

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    status, result = pf.set_pet_photo(auth_key, petid, pet_photo )

    assert status == 200
    assert result['pet_photo'] != ''






def test_get_my_pets(filter='my_pets'):
    """ Проверяем что выводится список  личных питомцев."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(result['pets']) > 0:
        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert len(result['pets']) > 0
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


