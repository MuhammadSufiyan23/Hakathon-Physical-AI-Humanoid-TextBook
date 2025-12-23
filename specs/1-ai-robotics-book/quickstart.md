# Quickstart Guide: AI-native technical textbook on Physical AI & Humanoid Robotics

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager
- Python 3.8+ (for ROS2 examples)
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd humanoid-robotics-book
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
NEON_DATABASE_URL=your_neon_database_url
BETTER_AUTH_SECRET=your_auth_secret
BETTER_AUTH_URL=http://localhost:3000
```

### 4. Initialize the Database

```bash
# Run database migrations
npx prisma db push
# Generate Prisma client
npx prisma generate
```

### 5. Run the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Project Structure

- `docs/` - Contains all textbook content in Markdown format
  - `weekly/` - Weekly content (Weeks 1-13)
  - `physical-ai/` - Additional Physical AI content
- `src/` - Custom React components and theme files
- `static/` - Static assets like images
- `docusaurus.config.js` - Main Docusaurus configuration
- `sidebars.js` - Navigation sidebar configuration

## Adding New Content

### To add a new chapter:

1. Create a new Markdown file in the appropriate directory under `docs/`
2. Add the content using Docusaurus Markdown syntax
3. Update `sidebars.js` to include the new page in the navigation

### To add code examples:

Include code blocks in your Markdown files with appropriate language tags:

```python
# Python ROS2 example
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher = self.create_publisher(String, 'topic', 10)
```

## Building for Production

```bash
npm run build
```

This will generate a static site in the `build/` directory that can be deployed to Vercel, GitHub Pages, or other static hosting platforms.

## Running Tests

```bash
npm run test
```

## Deployment

The project is configured for deployment to Vercel or GitHub Pages. Follow the respective platform's documentation for deployment instructions, ensuring that environment variables are properly configured.