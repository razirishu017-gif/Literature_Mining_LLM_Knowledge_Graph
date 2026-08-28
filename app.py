import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Insight Engine: Digital Media & Well-being", layout="wide")
st.title("🧠 Digital Media & Well-Being: Insight Engine")
st.markdown("Ask the graph a question or select a concept to instantly visualize the clinical evidence.")

# 2. Load Data
@st.cache_data
def load_data():
    with open("data/normalized_graph_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# Extract all unique nodes (concepts) for the search bar
unique_nodes = set()
for item in data:
    unique_nodes.add(item["intervention"])
    unique_nodes.add(item["outcome"])
unique_nodes = sorted(list(unique_nodes))

# 3. Session State for "One-Click" Query Buttons
if "search_query" not in st.session_state:
    st.session_state.search_query = "Depression" # Default starting view

# 4. Sidebar - Metrics & Preset Questions
st.sidebar.header("📊 Pipeline Validation")
st.sidebar.metric(label="Extraction Precision", value="90.0%")
st.sidebar.metric(label="Extraction Recall", value="87.5%")
st.sidebar.metric(label="Final F1-Score", value="88.7%")

st.sidebar.markdown("---")
st.sidebar.header("💡 Ask the Graph")
st.sidebar.caption("Click a question to instantly query the network:")

# Preset query buttons that update the session state
if st.sidebar.button("🔍 What reduces Loneliness?"):
    st.session_state.search_query = "Loneliness"
if st.sidebar.button("🔍 What are the risks of FOMO?"):
    st.session_state.search_query = "Fear Of Missing Out"
if st.sidebar.button("🔍 Show me Digital Detox effects"):
    st.session_state.search_query = "Digital Detox"
if st.sidebar.button("🔍 What increases Anxiety?"):
    st.session_state.search_query = "Anxiety"

# 5. Main Search Bar (The "Free-Text" Query Box)
user_query = st.text_input(
    "💬 Type your question in plain English (e.g., 'What are the effects of Smartphone Addiction?'):", 
    value=""
)

# 5b. NLP Simulation: Find matching concepts in their typed question
if user_query:
    found_match = False
    # Sort nodes by length descending so it matches "Social Media Addiction" before "Social Media"
    for node in sorted(unique_nodes, key=len, reverse=True):
        if node.lower() in user_query.lower():
            st.session_state.search_query = node
            found_match = True
            break
            
    if found_match:
        st.success(f"Graph filtered for: **{st.session_state.search_query}**")
    else:
        st.warning("Hmm, I couldn't find a direct clinical match for that in the graph. Try asking about a specific concept like 'Screen Time', 'Anxiety', or 'Sleep Quality'.")

# 5c. Fallback Dropdown (for manual browsing)
selected_node = st.selectbox(
    "Or browse all available concepts in the database:",
    options=["-- Show Full Network --"] + unique_nodes,
    index=unique_nodes.index(st.session_state.search_query) + 1 if st.session_state.search_query in unique_nodes else 0
)

# Sync selectbox with session state (only if they are using the dropdown instead of the search bar)
if selected_node != "-- Show Full Network --" and not user_query:
    st.session_state.search_query = selected_node

# 6. Filter Data (Ego-Network Logic)
if selected_node == "-- Show Full Network --":
    filtered_data = data
else:
    # Only keep triplets where the selected node is the intervention OR the outcome
    filtered_data = [d for d in data if d["intervention"] == selected_node or d["outcome"] == selected_node]

# 7. Build the NetworkX Graph
G = nx.DiGraph()

for item in filtered_data:
    source = item["intervention"]
    target = item["outcome"]
    rel = item["relationship"]
    paper = item["source_paper"]
    
    # Dynamic Coloring & Sizing (Highlight the queried node in Red, make it larger)
    source_color = "#E63946" if source == selected_node else "#4C72B0"
    target_color = "#E63946" if target == selected_node else "#DD8452"
    
    source_size = 30 if source == selected_node else 15
    target_size = 30 if target == selected_node else 15
    
    G.add_node(source, title="Intervention", color=source_color, size=source_size)
    G.add_node(target, title="Outcome", color=target_color, size=target_size)
    
    # Add the directed edge
    G.add_edge(source, target, label=rel, title=f"Source: {paper}")

# 8. Layout: Graph on the left, Plain-English summaries on the right
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### 🕸️ Network View: **{selected_node}**")
    
    # Initialize PyVis network (Dark mode background)
    net = Network(height="600px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
    net.from_nx(G)
    net.repulsion(node_distance=150, central_gravity=0.1, spring_length=150, spring_strength=0.05, damping=0.09)
    net.save_graph("knowledge_graph.html")
    
    # Render Graph
    HtmlFile = open("knowledge_graph.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=650)

with col2:
    st.markdown("### 🤖 The Engine's Answer")
    st.caption("A plain-English synthesis of the clinical literature.")
    
    if len(filtered_data) == 0:
        st.write("I couldn't find a direct clinical answer in the current literature database.")
    else:
        # 1. Did the user ask about TWO concepts?
        secondary_match = None
        if user_query:
            # FIX: Erase the first concept from the search string so we don't accidentally match a substring of it!
            remaining_query = user_query.lower().replace(selected_node.lower(), "")
            
            for node in sorted(unique_nodes, key=len, reverse=True):
                # Now we search the remaining sentence for a second node
                if node.lower() in remaining_query:
                    secondary_match = node
                    break
        
        # 2. If they asked about two specific things, give a direct, conversational "Yes/No" answer
        if secondary_match:
            # Look for the exact arrow between these two concepts
            direct_links = [d for d in filtered_data if (d["intervention"] == secondary_match or d["outcome"] == secondary_match)]
            
            if direct_links:
                st.success(f"**Yes!** I found a direct clinical relationship between **{selected_node}** and **{secondary_match}**.")
                
                seen_responses = set()
                for link in direct_links:
                    paper_name = link['source_paper'].replace('.grobid.txt', '')
                    intervention = link['intervention']
                    outcome = link['outcome']
                    relationship = link['relationship'].replace('_', ' ')
                    
                    response_sentence = f"As per the research in *{paper_name}*, we know that **{intervention}** actually **{relationship}** **{outcome}**."
                    
                    if response_sentence not in seen_responses:
                        st.write(response_sentence)
                        seen_responses.add(response_sentence)
            else:
                st.warning(f"I understand you are asking about **{selected_node}** and **{secondary_match}**. However, this specific dataset does not contain a direct clinical link between those two concepts.")
        
        # 3. If they just asked about ONE concept, provide the general bulleted summary
        else:
            st.write(f"Based on the literature, here is how **{selected_node}** interacts with other clinical factors:")
            for item in filtered_data:
                rel = item['relationship'].replace('_', ' ')
                paper_name = item['source_paper'].replace('.grobid.txt', '')
                
                # Color coding the relationship logic
                if rel in ['reduces', 'decreases', 'treats', 'improves']:
                    color = "#2ca02c" # Green
                elif rel in ['increases', 'worsens', 'causes']:
                    color = "#d62728" # Red
                else:
                    color = "#ffffff" # White
                    
                st.markdown(f"- **{item['intervention']}** <span style='color:{color};'>**{rel}**</span> **{item['outcome']}**  \n*(Source: {paper_name})*", unsafe_allow_html=True)