import streamlit as st
import os
import json
import sys

# Lazy load heavy imports to improve cold start time
# These will be imported only when needed

# Add error handling for missing environment variables
def check_environment():
    """Check if required environment variables are set"""
    missing_vars = []
    if not os.environ.get("GROQ_API_KEY"):
        missing_vars.append("GROQ_API_KEY")

    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.info("Please set GROQ_API_KEY in your Streamlit secrets or environment variables.")
        return False
    return True

# Page configuration
st.set_page_config(
    page_title="SecondSelf - Personal AI Second Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme CSS
st.markdown("""
<style>
    /* Use system fonts for faster loading */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stAppViewBlock { display: none; }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #4a4a6a;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6a6a8a;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Logo and branding */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    .logo-tagline {
        font-size: 0.75rem;
        color: #8888aa;
        margin-top: 2px;
    }
    
    /* Navigation buttons */
    .nav-button {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        margin: 4px 12px;
        border-radius: 12px;
        background: transparent;
        color: #a0a0c0;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .nav-button:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #ffffff;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        color: #ffffff;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .nav-icon {
        font-size: 1.2rem;
    }
    
    /* Card styling */
    .card {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.8) 0%, rgba(15, 15, 26, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .card-subtitle {
        font-size: 0.85rem;
        color: #8888aa;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.02);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #8888aa;
        margin-top: 0.5rem;
    }
    
    /* Chat interface styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
    }
    
    .chat-message {
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        border-radius: 16px;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin-left: 2rem;
    }
    
    .chat-message.assistant {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-right: 2rem;
    }
    
    .chat-message-content {
        color: #e0e0e0;
        line-height: 1.6;
    }
    
    /* Input styling */
    .stChatInput {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Graph container */
    .graph-container {
        background: rgba(15, 15, 26, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Header styling */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .page-subtitle {
        font-size: 0.9rem;
        color: #8888aa;
    }
    
    /* Tag styling */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 2px;
        background: rgba(102, 126, 234, 0.2);
        color: #a0a0ff;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .section-icon {
        font-size: 1.2rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: #8888aa;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .chat-message.user {
            margin-left: 0.5rem;
        }
        .chat-message.assistant {
            margin-right: 0.5rem;
        }
    }
    
    /* Capture card styling */
    .capture-card {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.9) 0%, rgba(15, 15, 26, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0.75rem 1rem 0.75rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .capture-card:hover {
        border-color: rgba(102, 126, 234, 0.2);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.1);
    }
    
    .capture-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.25rem;
        letter-spacing: -0.3px;
    }
    
    .capture-label {
        font-size: 0.75rem;
        color: #8888aa;
        margin-bottom: 0.75rem;
        font-weight: 400;
    }
    
    /* Capture textarea styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        font-size: 0.9rem !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
        resize: none !important;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(102, 126, 234, 0.4) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #666688 !important;
    }
    
    /* Capture button styling */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #7a8ff4 0%, #8a5cb6 100%) !important;
    }
    
    div[data-testid="stButton"] > button:active {
        transform: translateY(0) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG engine (lazy-loaded and cached)
@st.cache_resource
def get_rag_engine():
    """Get or create RAG engine instance with resource caching"""
    # Trigger reload to load fresh embeddings from git
    from ask import RAGEngine
    return RAGEngine()

def clear_rag_engine():
    """Clear the cached RAG engine to force reload with fresh embeddings"""
    # Clear the encoder cache for memory management
    try:
        from ask import RAGEngine
        RAGEngine.clear_encoder_cache()
    except:
        pass  # Handle case where RAGEngine not yet imported

    # Clear Streamlit cache
    get_rag_engine.clear()

    # Clear sidebar graph cache
    if "sidebar_graph_data" in st.session_state:
        del st.session_state.sidebar_graph_data

    # Clear graph cache
    load_graph.clear()

@st.cache_data(ttl=300)  # Cache for 5 minutes to balance freshness and performance
def load_graph():
    """Load the knowledge graph from graph.json with caching"""
    graph_file = os.path.join(os.path.dirname(__file__), 'graph.json')
    if os.path.exists(graph_file):
        try:
            with open(graph_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading graph: {e}")
            return None
    return None

def run_pipeline(force_reprocess=False):
    """Run the complete pipeline: classify, link, and build graph"""
    import glob
    import sys
    import os
    import time
    
    raw_dir = os.path.join(os.path.dirname(__file__), 'raw')
    wiki_dir = os.path.join(os.path.dirname(__file__), 'wiki')
    
    # Step 1: Classify raw files
    raw_files = glob.glob(os.path.join(raw_dir, '*.txt'))
    
    if not raw_files:
        return "No raw files to process."
    
    try:
        start_time = time.time()
        
        # Import and run classify
        sys.path.insert(0, os.path.dirname(__file__))
        from classify import process_files
        classify_start = time.time()
        process_files()
        classify_time = time.time() - classify_start
        
        # Step 2: Link related notes (this generates embeddings)
        from link import process_links
        link_start = time.time()
        process_links()
        link_time = time.time() - link_start
        
        # Step 3: Build graph
        from build_graph import build_graph
        graph_start = time.time()
        build_graph()
        graph_time = time.time() - graph_start
        
        total_time = time.time() - start_time
        return f"Successfully processed {len(raw_files)} files through the pipeline.\n⏱️ Timing: Classify: {classify_time:.1f}s, Link: {link_time:.1f}s, Graph: {graph_time:.1f}s, Total: {total_time:.1f}s\nNew notes are now available in chat and knowledge graph."
    except Exception as e:
        return f"Pipeline error: {str(e)}"


def render_sidebar():
    """Render the premium sidebar with navigation"""
    with st.sidebar:
        # Logo section
        st.markdown("""
        <div class="logo-container">
            <div class="logo-icon">🧠</div>
            <div>
                <div class="logo-text">SecondSelf</div>
                <div class="logo-tagline">Your Personal AI Second Brain</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div style="padding: 0.5rem 0;">', unsafe_allow_html=True)
        
        if st.session_state.get('current_page') == 'chat':
            st.markdown('<button class="nav-button active"><span class="nav-icon">💬</span> Chat</button>', unsafe_allow_html=True)
        else:
            if st.button('💬 Chat', key='nav_chat', help='Chat with your second brain'):
                st.session_state.current_page = 'chat'
                st.rerun()
        
        if st.session_state.get('current_page') == 'graph':
            st.markdown('<button class="nav-button active"><span class="nav-icon">🕸️</span> Knowledge Graph</button>', unsafe_allow_html=True)
        else:
            if st.button('🕸️ Knowledge Graph', key='nav_graph', help='Visualize your knowledge'):
                st.session_state.current_page = 'graph'
                st.rerun()
        
        if st.session_state.get('current_page') == 'stats':
            st.markdown('<button class="nav-button active"><span class="nav-icon">📊</span> Statistics</button>', unsafe_allow_html=True)
        else:
            if st.button('📊 Statistics', key='nav_stats', help='View your statistics'):
                st.session_state.current_page = 'stats'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Capture Note Section
        st.markdown('<div class="section-header"><span class="section-icon">✨</span> Capture</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="capture-card">
            <div class="capture-title">Capture Note</div>
            <div class="capture-label">Quick Note</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize capture session state variables
        if "capture_success" not in st.session_state:
            st.session_state.capture_success = False
        if "capture_error" not in st.session_state:
            st.session_state.capture_error = None
        
        # Capture input and button using form for proper submission
        with st.form(key="capture_form", clear_on_submit=True):
            note_input = st.text_area(
                "Capture Note",
                placeholder="Capture a thought, task, or insight...",
                key="capture_note_text",
                height=100,
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button(
                "Capture Note",
                use_container_width=True
            )
            
            if submitted and note_input and note_input.strip():
                try:
                    import sys
                    import os
                    sys.path.insert(0, os.path.dirname(__file__))
                    from capture import capture
                    
                    capture(note_input.strip())
                    st.success("✓ Note captured successfully!")
                except Exception as e:
                    st.error(f"Failed to capture note: {str(e)}")
        
        st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

        # Pipeline section
        st.markdown('<div class="section-header"><span class="section-icon">⚙️</span> Pipeline</div>', unsafe_allow_html=True)
        force_reprocess = st.checkbox("Force re-process")
        if st.button("Process new captures", use_container_width=True):
            with st.spinner("Processing pipeline..."):
                result = run_pipeline(force_reprocess)
                if "Successfully" in result:
                    st.success(result)
                    # Force graph reload by clearing any cached data
                    if "graph_data" in st.session_state:
                        del st.session_state.graph_data
                    # Force sidebar graph cache clear
                    if "sidebar_graph_data" in st.session_state:
                        del st.session_state.sidebar_graph_data
                    # Force RAG engine reload to pick up fresh embeddings
                    clear_rag_engine()
                    st.rerun()
                else:
                    st.error(result)
        
        st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
        
        # Quick stats in sidebar
        st.markdown('<div class="section-header"><span class="section-icon">⚡</span> Quick Stats</div>', unsafe_allow_html=True)
        
        # Lazy load graph data for sidebar stats
        if "sidebar_graph_data" not in st.session_state:
            st.session_state.sidebar_graph_data = load_graph()
        
        graph_data = st.session_state.sidebar_graph_data
        if graph_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Notes", len(graph_data.get("nodes", [])))
            with col2:
                st.metric("Links", len(graph_data.get("edges", [])))
        
        st.markdown('<div style="margin-top: auto; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.75rem; color: #666688;">Powered by AI</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_page():
    """Render the premium chat interface"""
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">💬 Chat with Your Second Brain</div>
            <div class="page-subtitle">Ask questions about your notes and get intelligent answers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Custom chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages with custom styling
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user fade-in">
                    <div class="chat-message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant fade-in">
                    <div class="chat-message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div style="padding: 1rem 0;">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Ask your second brain a question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.spinner("🔍 Searching your knowledge base..."):
            try:
                engine = get_rag_engine()
                response = engine.ask(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_graph_page():
    """Render the premium knowledge graph visualization"""
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">🕸️ Knowledge Graph</div>
            <div class="page-subtitle">Visualize the connections between your notes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    graph_data = load_graph()
    
    if graph_data and graph_data.get("nodes"):
        # Lazy import graph library to speed up initial page load
        try:
            from streamlit_agraph import Node, Edge, Config, agraph
        except ImportError:
            st.error("streamlit-agraph library not found. Please install it with: pip install streamlit-agraph")
            return
        except Exception as e:
            st.error(f"Error loading graph library: {e}")
            return
        
        nodes = []
        edges = []
        
        # Create nodes with enhanced styling
        for node_data in graph_data["nodes"]:
            # Size based on connections
            node_connections = sum(1 for edge in graph_data["edges"] 
                                   if edge["source"] == node_data["id"] or edge["target"] == node_data["id"])
            size = 20 + min(node_connections * 2, 15)
            
            # Color based on group
            group_colors = {
                "Projects": "#667eea",
                "Resources": "#764ba2", 
                "Areas": "#f093fb",
                "Uncategorized": "#8888aa"
            }
            color = group_colors.get(node_data.get("group", "Uncategorized"), "#8888aa")
            
            node = Node(
                id=node_data["id"],
                label=node_data["label"][:30] + "..." if len(node_data["label"]) > 30 else node_data["label"],
                title=f"{node_data.get('title', '')}\nGroup: {node_data.get('group', 'Uncategorized')}",
                group=node_data.get("group", "Uncategorized"),
                size=size,
                color=color,
                x=node_data.get("x"),
                y=node_data.get("y")
            )
            nodes.append(node)
        
        # Create edges
        for edge_data in graph_data["edges"]:
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                label="",
                width=2,
                color="#4a4a6a"
            )
            edges.append(edge)
        
        # Enhanced graph configuration
        config = Config(
            width=1200,
            height=700,
            directed=False,
            physics=False,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#667eea"
        )
        
        # Graph container
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        agraph(nodes=nodes, edges=edges, config=config)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced statistics section
        st.markdown('<div class="section-header"><span class="section-icon">📊</span> Network Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(graph_data["nodes"])}</div>
                <div class="metric-label">Total Notes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(graph_data["edges"])}</div>
                <div class="metric-label">Connections</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            categories = len(set(node.get("group", "Uncategorized") for node in graph_data["nodes"]))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{categories}</div>
                <div class="metric-label">Categories</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Calculate average connections
            avg_connections = len(graph_data["edges"]) / len(graph_data["nodes"]) if graph_data["nodes"] else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_connections:.1f}</div>
                <div class="metric-label">Avg Connections</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Group breakdown
        st.markdown('<div class="section-header"><span class="section-icon">📁</span> Content by Category</div>', unsafe_allow_html=True)
        
        group_counts = {}
        for node in graph_data["nodes"]:
            group = node.get("group", "Uncategorized")
            group_counts[group] = group_counts.get(group, 0) + 1
        
        for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(graph_data["nodes"])) * 100
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="card-title">{group}</div>
                        <div class="card-subtitle">{count} notes</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">{percentage:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.markdown("""
        <div class="card">
            <div class="card-title">No Graph Data Found</div>
            <div class="card-subtitle">Please run the graph building script first</div>
            <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 8px; font-family: monospace; color: #a0a0ff;">
                python build_graph.py
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_stats_page():
    """Render the statistics dashboard"""
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">📊 Statistics Dashboard</div>
            <div class="page-subtitle">Overview of your knowledge base</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    graph_data = load_graph()
    
    if graph_data and graph_data.get("nodes"):
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(graph_data["nodes"])}</div>
                <div class="metric-label">Total Notes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(graph_data["edges"])}</div>
                <div class="metric-label">Total Connections</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            categories = len(set(node.get("group", "Uncategorized") for node in graph_data["nodes"]))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{categories}</div>
                <div class="metric-label">Categories</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_tags = sum(len(node.get("tags", [])) for node in graph_data["nodes"])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_tags}</div>
                <div class="metric-label">Total Tags</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Category breakdown
        st.markdown('<div class="section-header"><span class="section-icon">📁</span> Content Distribution</div>', unsafe_allow_html=True)
        
        group_counts = {}
        for node in graph_data["nodes"]:
            group = node.get("group", "Uncategorized")
            group_counts[group] = group_counts.get(group, 0) + 1
        
        cols = st.columns(min(len(group_counts), 3))
        for idx, (group, count) in enumerate(sorted(group_counts.items(), key=lambda x: x[1], reverse=True)):
            with cols[idx % 3]:
                percentage = (count / len(graph_data["nodes"])) * 100
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{group}</div>
                    <div class="card-subtitle">{count} notes · {percentage:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Popular tags
        st.markdown('<div class="section-header"><span class="section-icon">🏷️</span> Popular Tags</div>', unsafe_allow_html=True)
        
        tag_counts = {}
        for node in graph_data["nodes"]:
            for tag in node.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:12]
        
        tag_cols = st.columns(4)
        for idx, (tag, count) in enumerate(top_tags):
            with tag_cols[idx % 4]:
                st.markdown(f'<span class="tag">{tag} ({count})</span>', unsafe_allow_html=True)
        
        # Most connected notes
        st.markdown('<div class="section-header"><span class="section-icon">🔗</span> Most Connected Notes</div>', unsafe_allow_html=True)
        
        connection_counts = {}
        for edge in graph_data["edges"]:
            connection_counts[edge["source"]] = connection_counts.get(edge["source"], 0) + 1
            connection_counts[edge["target"]] = connection_counts.get(edge["target"], 0) + 1
        
        top_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for node_id, count in top_connected:
            node = next((n for n in graph_data["nodes"] if n["id"] == node_id), None)
            if node:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{node['label'][:50]}...</div>
                    <div class="card-subtitle">{count} connections · {node.get('group', 'Uncategorized')}</div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="card">
            <div class="card-title">No Data Available</div>
            <div class="card-subtitle">Please build your knowledge graph first</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Check environment variables
    if not check_environment():
        st.stop()

    # Initialize current page if not exists
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"

    # Render sidebar
    render_sidebar()

    # Main content area - lazy load pages based on navigation
    if st.session_state.current_page == "chat":
        render_chat_page()
    elif st.session_state.current_page == "graph":
        render_graph_page()
    elif st.session_state.current_page == "stats":
        render_stats_page()

if __name__ == "__main__":
    main()