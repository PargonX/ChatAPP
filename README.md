# Flask Chat Application

This is a simple chat application built with Flask, SQLAlchemy, Flask-SocketIO, and Flask-Mail. It allows users to register, log in, send messages in a chat room, and verify their email addresses.

## Features

- User registration and login system
- Email verification for newly registered users
- Reset password functionality
- Real-time messaging using WebSocket with Flask-SocketIO
- Simple chat interface
- Ability to clear chat history

## Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/your_username/your_repository.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure your application by editing the `config.yml` file. Make sure to set up your mail server details and secret key.

4. Run the application:

    ```bash
    python app.py
    ```

5. Access the application in your web browser at `http://localhost:5000`.

## Usage

- Register a new account by providing a username, email, and password.
- Verify your email address by clicking on the verification link sent to your email.
- Log in with your registered username or email and password.
- Send messages in the chat room.
- Click on the "Logout" button to log out of your account.
- Click on the "Clear Chat" button to delete all chat history.

## File Structure

- `app.py`: Main Flask application file containing routes and WebSocket handling.
- `config.yml`: Configuration file for the application, including database and mail server settings.
- `templates/`: Directory containing HTML templates for the application.
- `static/`: Directory containing static files such as CSS and JavaScript.

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-SocketIO
- Flask-Mail

## Contributing

Contributions are welcome! If you find any bugs or want to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

[PargonX](https://github.com/PargonX)

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [itsdangerous](https://pypi.org/project/itsdangerous/)
- [Werkzeug](https://werkzeug.palletsprojects.com/)
