# SecondSelf - Premium AI Second Brain Dashboard

A sophisticated, production-ready AI-powered personal knowledge management system built with Streamlit, featuring a premium dark theme inspired by Notion AI, Obsidian, and ChatGPT.

## ✨ Features

### 🎨 Premium UI/UX
- **Professional Dark Theme**: Modern gradient-based design with glassmorphism effects
- **Fixed Sidebar Navigation**: Intuitive navigation with animated transitions
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Fade-in effects, hover states, and micro-interactions
- **Custom Scrollbars**: Styled scrollbars matching the dark theme

### 💬 Chat Interface
- **Real-time AI Chat**: Interact with your personal knowledge base using natural language
- **Context-Aware Responses**: Powered by RAG (Retrieval-Augmented Generation) using Groq API
- **Message History**: Persistent chat sessions with role-based styling
- **Loading States**: Elegant loading indicators during knowledge retrieval

### 🕸️ Knowledge Graph
- **Interactive Visualization**: Dynamic network graph using streamlit-agraph
- **Node Styling**: Size and color-coded nodes based on connections and categories
- **Physics-Based Layout**: Automatic graph arrangement with smooth animations
- **Enhanced Statistics**: Real-time network metrics and category breakdown

### 📊 Statistics Dashboard
- **Key Metrics**: Total notes, connections, categories, and tags
- **Content Distribution**: Visual breakdown by category with percentages
- **Popular Tags**: Cloud display of most used tags
- **Connection Analysis**: Most connected notes and network density

### 🔧 Technical Features
- **Modular Architecture**: Clean separation of UI components and backend logic
- **Cached Components**: Optimized performance with Streamlit caching
- **Error Handling**: Graceful error messages and fallback states
- **Production-Ready**: Suitable for portfolio showcases and demonstrations

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Second-self
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

4. Build your knowledge graph:
```bash
python build_graph.py
```

5. Run the application:
```bash
streamlit run app.py
```

## 📁 Project Structure

```
Second-self/
├── app.py                    # Main Streamlit application with premium UI
├── ask.py                    # RAG engine for AI-powered search
├── build_graph.py            # Knowledge graph construction
├── convert_to_obsidian.py    # Export to Obsidian format
├── data/
│   └── embeddings.pkl        # Pre-computed embeddings
├── graph.json                # Knowledge graph data
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Usage

### Chat with Your Second Brain
1. Navigate to the "Chat" tab in the sidebar
2. Type your question in the input field
3. Receive context-aware answers from your personal knowledge base

### Explore Knowledge Graph
1. Click on "Knowledge Graph" in the sidebar
2. Interact with the network visualization
3. View detailed statistics and category breakdowns

### View Statistics
1. Access the "Statistics" page
2. Review comprehensive metrics about your knowledge base
3. Analyze content distribution and connection patterns

## 🎨 Design System

### Color Palette
- **Primary Gradient**: #667eea to #764ba2
- **Background**: #0f0f1a to #1a1a2e
- **Card Background**: rgba(26, 26, 46, 0.8)
- **Text Primary**: #ffffff
- **Text Secondary**: #8888aa
- **Accent**: #667eea

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 600-700 weight
- **Body**: 400-500 weight
- **Sizes**: 0.75rem to 2rem

### Components
- **Cards**: Rounded corners (16px), glassmorphism effect
- **Buttons**: Gradient backgrounds, hover states
- **Inputs**: Minimal styling with focus states
- **Metrics**: Large values with gradient text

## 🔌 Backend Integration

The application maintains the original backend logic from `ask.py`:
- **Sentence Transformers**: all-MiniLM-L6-v2 for embeddings
- **Groq API**: Llama-3.1-8b-instant model for responses
- **Vector Search**: Cosine similarity for relevant document retrieval
- **Caching**: Optimized model loading and data access

## 📊 Performance Optimizations

- **Resource Caching**: RAG engine cached with `@st.cache_resource`
- **Lazy Loading**: Models loaded only when needed
- **Efficient Rendering**: Minimal re-renders with proper state management
- **Optimized Graph**: Efficient node and edge rendering

## 🌐 Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🚧 Future Enhancements

- [ ] User authentication and personalization
- [ ] Real-time collaboration features
- [ ] Advanced graph filtering and search
- [ ] Export to additional formats (Notion, Roam Research)
- [ ] Voice input/output capabilities
- [ ] Mobile app version

## 📝 License

This project is open source and available for educational and portfolio purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Streamlit, Python, and AI**
