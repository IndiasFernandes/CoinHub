
# CoinHub: Trading Strategy Backtesting and Optimization Platform

CoinHub is a robust Django-based platform designed to backtest and optimize trading strategies using historical data. This application allows users to evaluate the performance of trading strategies under various settings and find the most effective configurations.

## Key Features

- **Backtesting**: Simulate trading strategies using historical data to assess performance metrics.
- **Optimization**: Automatically adjust strategy parameters to maximize performance indicators like Sharpe Ratio.
- **User Accounts**: Secure authentication system for managing user sessions.
- **Interactive Results**: View detailed results and summaries of backtests and optimizations.
- **Data Management**: Interface for uploading, downloading, and managing historical price data.

## Project Structure

```
CoinHub/
│
├── apps/
│   ├── accounts/            - User authentication and management.
│   ├── bots/                - Trading bots management and operations.
│   ├── exchanges/           - Handling of exchange data and interactions.
│   ├── market/              - Core functionality for backtesting and optimization.
│
├── CoinHub/                 - Project settings and configurations.
├── static/                  - Static files for styling and JS scripts.
├── templates/               - HTML templates for rendering views.
└── requirements.txt         - Project dependencies.
```

## Getting Started

### Prerequisites

- Python 3.8+
- Django 3.2+
- Other dependencies are listed in `requirements.txt`.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/CoinHub.git
   cd CoinHub
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Usage

- Navigate to `http://127.0.0.1:8000/` in your web browser to access the application.
- Log in using the superuser credentials to access the dashboard.
- Follow the UI prompts to upload data, run backtests, or perform optimizations.

## Development

### Adding New Features

- To add new features or strategies, extend the models in `apps/market/models.py` and include relevant business logic in `views.py`.
- Use Django admin to add or modify resources dynamically.

### Testing

- Ensure to write tests for new features under `tests/` directory.
- Run tests using:
  ```bash
  python manage.py test
  ```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests to the project.

## License

Distributed under the MIT License. See [LICENSE](LICENSE.md) for more information.

## Contact

Daniel Indias - daniel.indias@innerflect.com

Project Link: [https://github.com/IndiasFernandes/CoinHub](https://github.com/IndiasFernandes/CoinHub)
