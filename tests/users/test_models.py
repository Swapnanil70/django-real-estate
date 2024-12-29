import pytest

def test_user_str(base_user):
    """Test the custom user model string representation"""
    assert base_user.__str__() == f"{base_user.username}"
    
def test_user_short_name(base_user):
    """Test tat the user models get short name method works"""
    short_name = f"{base_user.username}"
    assert base_user.get_short_name() == short_name
    
def test_user_full_name(base_user):
    """Test that the user models get full name method works"""
    full_name = f"{base_user.first_name} {base_user.last_name}"
    assert base_user.get_full_name == full_name 
    
def test_base_user_email_is_normalized(base_user):
    """Test that the user models email is normalized"""
    email = "neel@GmAIL.com"
    assert base_user.email == email.lower()
    
def test_super_user_email_is_normalized(super_user):
    """Test that the super user models email is normalized"""
    email = "neel@GmAIL.com"
    assert super_user.email == email.lower()
    
def test_superuser_is_staff(user_factory):
    """Test an error is raised when creating a superuser with is_staff=False"""
    with pytest.raises(ValueError) as err: 
        user_factory.create(is_staff=False, is_superuser=True)
    assert str(err.value) == "Superuser must have is_staff=True"
    
def test_super_user_is_not_superuser(user_factory):
    """Test an error is raised when creating a superuser with is_superuser=False"""
    with pytest.raises(ValueError) as err: 
        user_factory.create(is_staff=True, is_superuser=False)
    assert str(err.value) == "Superuser must have is_superuser=True"
    
def test_create_user_with_no_email(user_factory):
    """Test that creating a new user with no email address raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(email=None)
    assert str(err.value) == "Base User Account : You must provide an email address"


def test_create_use_with_no_username(user_factory):
    """Test that creating a new user with no usrname raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(username=None)
    assert str(err.value) == "The Username field must be filled"


def test_create_user_with_no_firstname(user_factory):
    """Test creating a new user without a firstname raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(first_name=None)
    assert str(err.value) == "The First Name field must be filled"


def test_create_user_with_no_lastname(user_factory):
    """Test creating a new user without a lastname raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(last_name=None)
    assert str(err.value) == "The Last Name field must be filled"


def test_create_superuser_with_no_email(user_factory):
    """Test creating a superuser without an email address raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(email=None, is_superuser=True, is_staff=True)
    assert str(err.value) == "Admin Account : You must provide an email address"


def test_create_superuser_with_no_password(user_factory):
    """Test creating a superuser without a password raises an error"""
    with pytest.raises(ValueError) as err:
        user_factory.create(is_superuser=True, is_staff=True, password=None)
    assert str(err.value) == "Superuser must have a password"


def test_user_email_incorrect(user_factory):
    """Test that an Error is raised when a non valid email is provided"""
    with pytest.raises(ValueError) as err:
        user_factory.create(email="realestate.com")
    assert str(err.value) == "You must provide a valid email address"