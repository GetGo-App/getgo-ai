# GetGo AI

## About The Project

GetGo AI is an artificial intelligence model designed to enhance the travel planning experience for users of the GetGo platform. This model leverages natural language processing and machine learning techniques to provide personalized destination recommendations, generate optimized itineraries, and offer intelligent travel advice.

## Features

- **Personalized Route Creation:** Designs unique travel routes tailored to the user's specific preferences, budget, interests, and time constraints.
- **Location Information:** Provides comprehensive details about destinations, including attractions, accommodations, dining options, local customs, and transportation options.
- **Travel Tips and Advice:** Offers practical tips for efficient travel, safety precautions, cultural insights, and suggestions for off-the-beaten-path experiences.
- **Interactive Q&A:** Engages in natural language conversations with users, answering their questions about destinations, itineraries, travel planning, and more.
- **Multilingual Support:** Understands and responds in multiple languages to cater to a global user base.
- **Real-time Updates:** Provides up-to-date information on travel restrictions, weather conditions, and local events that may impact travel plans. 

## Getting Started

### Prerequisites

- Python 3.10
- Required libraries (listed in `requirements.txt`)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/pphuc25/GetGo-AI.git
    ```
2. Start Searxng
    ```
    cd searxng-docker & docker-compose up -d
    ```
3.  Configure Environment Variables:
- Open the .env file in the project root directory.
- Replace placeholders with your actual API keys and values:
    ```
    OPENAI_API_KEY=your_openai_api_key
    YOUR_API_HEADER_KEY=your_api_header_key
    SEARXNG_PORT=your_searxng_port
    ```
4. Build and run the Docker container of GetGo AI:
    ```bash
    docker build -t GetGo-AI .
    docker run -p 7860:7860 GetGo-AI
    ```

## Contact

Phuc Phan - phanphuc1100@gmail.com
