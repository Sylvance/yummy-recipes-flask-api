""" User, Category and Recipes models"""
from app import APP, DB, BCRYPT
import datetime
import jwt


class User(DB.Model):
    """ Table schema """
    __tablename__ = "users"

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    email = DB.Column(DB.String(255), unique=True, nullable=False)
    password = DB.Column(DB.String(255), nullable=False)
    bio = DB.Column(DB.String(255), nullable=False)
    joinedon = DB.Column(DB.DateTime, nullable=False)
    categories = DB.relationship('Category', backref='category', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = BCRYPT.generate_password_hash(password, APP.config.get('BCRYPT_HASH_PREFIX')) \
            .decode('utf-8')
        self.bio = "This is your bio. Describe your culinary prowess or preference."
        self.joinedon = datetime.datetime.now()

    def save(self):
        """ Persist the user in the database :param user: :return: """
        DB.session.add(self)
        DB.session.commit()
        return self.encode_token(self.id)

    def encode_token(self, user_id):
        """ Encode the Authentication token :param user_id: User's Id :return: """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=APP.config.get('TOKEN_EXPIRY_DAYS'),
                                                                       seconds=APP.config.get(
                                                                           'TOKEN_EXPIRY_SECONDS')),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                APP.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_token(token):
        """ Decoding the token to get the payload and then return the user Id in 'sub':param token: Authentication Token :return: """
        try:
            payload = jwt.decode(
                token, APP.config['SECRET_KEY'], algorithms='HS256')
            is_token_banned = BannedToken.check_banned(token)
            if is_token_banned:
                return 'Banned token, Please login In'
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Expired Signature, Please sign in again'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please sign in again'

    @staticmethod
    def get_by_id(user_id):
        """ Filter a user by Id. :param user_id: :return: User or None """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email):
        """ Check a user by their email address :param email: :return: """
        return User.query.filter_by(email=email).first()

    def reset_password(self, new_password):
        """ Update/reset the user password. :param new_password: New User Password :return: """
        self.password = new_password
        DB.session.commit()


class BannedToken(DB.Model):
    """ Table to store banneded/invalid auth tokens """
    __tablename__ = 'banned_token'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    token = DB.Column(DB.String(255), unique=True, nullable=False)
    banneded_on = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.banneded_on = datetime.datetime.now()

    def banned(self):
        """ Persist Banned token in the database :return: """
        DB.session.add(self)
        DB.session.commit()

    @staticmethod
    def check_banned(token):
        """ Check to find out whether a token has already been banned. :param token: Authorization token :return: """
        response = BannedToken.query.filter_by(token=token).first()
        if response:
            return True
        return False


class Category(DB.Model):
    """ Class to represent the Category model """
    __tablename__ = 'categories'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    name = DB.Column(DB.String(255), nullable=False)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    create_at = DB.Column(DB.DateTime, nullable=False)
    modified_at = DB.Column(DB.DateTime, nullable=False)
    recipes = DB.relationship('Recipe', backref='recipe', lazy='dynamic')

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.create_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ Persist a category in the database :return: """
        DB.session.add(self)
        DB.session.commit()

    def update(self, name):
        """ Update the name of the category :param name: :return: """
        self.name = name
        DB.session.commit()

    def delete(self):
        """ Delete a category from the database :return: """
        DB.session.delete(self)
        DB.session.commit()

    def json(self):
        """ Json representation of the category model. :return: """
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': self.create_at.isoformat(),
            'modifiedAt': self.modified_at.isoformat()
        }


class Recipe(DB.Model):
    """ Recipe model class """

    __tablename__ = 'recipes'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    name = DB.Column(DB.String(255), nullable=False)
    description = DB.Column(DB.Text, nullable=True)
    category_id = DB.Column(DB.Integer, DB.ForeignKey('category.id'))
    create_at = DB.Column(DB.DateTime, nullable=False)
    modified_at = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, name, description, category_id):
        self.name = name
        self.description = description
        self.category_id = category_id
        self.create_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ Persist Item into the database :return: """
        DB.session.add(self)
        DB.session.commit()

    def update(self, name, description=None):
        """ Update the records in the item :param name: Name :param description: Description :return: """
        self.name = name
        if description is not None:
            self.description = description
        DB.session.commit()

    def delete(self):
        """ Delete an item :return: """
        DB.session.delete(self)
        DB.session.commit()

    def json(self):
        """ Json representation of the model :return: """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categoryId': self.category_id,
            'createdAt': self.create_at.isoformat(),
            'modifiedAt': self.modified_at.isoformat()
        }
