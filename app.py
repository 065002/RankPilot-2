import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from seo_analyzer import analyze_page

# Page configuration (MUST be first Streamlit command)
st.set_page_config(
    page_title="SEO Analyzer Tool",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🔍 SEO Analyzer Tool")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
    1. Enter a complete URL (including https://)
    2. Click 'Analyze URL'
    3. Review your SEO metrics
    
    **Example URLs to test:**
    - https://example.com
    - https://python.org
    - https://wikipedia.org
    """)
    
    st.markdown("---")
    st.header("✅ What gets checked")
    st.markdown("""
    - Page Title & Meta Description
    - Heading Structure (H1-H6)
    - Images & Alt Text
    - Internal & External Links
    - Overall SEO Score
    """)
    
    st.markdown("---")
    st.caption("Built with Streamlit | SEO Analysis Tool v1.0")

# Main input area
col1, col2 = st.columns([3, 1])

with col1:
    url_input = st.text_input(
        "Enter Website URL:",
        placeholder="https://example.com",
        help="Include http:// or https://"
    )

with col2:
    analyze_button = st.button("🔍 Analyze URL", type="primary", use_container_width=True)

# Analysis logic
if analyze_button and url_input:
    with st.spinner("Analyzing webpage... This may take 10-15 seconds..."):
        results = analyze_page(url_input)
    
    # Check for errors
    if "Error" in results:
        st.error(f"❌ {results['Error']}")
        st.info("💡 Tips: Make sure the URL is correct and the website is accessible")
    else:
        # Display SEO Score prominently
        st.markdown("## 📊 SEO Performance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🎯 Overall SEO Score",
                value=f"{results['SEO_Score']}/100",
                delta="Good" if results['SEO_Score'] >= 70 else "Needs Improvement",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                label="📝 Title Length",
                value=f"{results['Title_Length']} chars",
                help="Optimal length: 30-60 characters"
            )
        
        with col3:
            st.metric(
                label="📄 Meta Description",
                value=f"{results['Meta_Description_Length']} chars",
                help="Optimal length: 50-160 characters"
            )
        
        st.markdown("---")
        
        # Create tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Meta Tags", 
            "📊 Headings", 
            "🖼️ Images", 
            "🔗 Links"
        ])
        
        # TAB 1: Meta Tags
        with tab1:
            st.subheader("Page Title")
            st.code(results['Title'], language="text")
            
            if results['Title_Length'] < 30:
                st.warning("⚠️ Title is too short (less than 30 characters)")
            elif results['Title_Length'] > 60:
                st.warning("⚠️ Title is too long (more than 60 characters)")
            else:
                st.success("✅ Title length is optimal (30-60 characters)")
            
            st.subheader("Meta Description")
            st.code(results['Meta_Description'], language="text")
            
            if results['Meta_Description_Length'] < 50:
                st.warning("⚠️ Meta description is too short (less than 50 characters)")
            elif results['Meta_Description_Length'] > 160:
                st.warning("⚠️ Meta description is too long (more than 160 characters)")
            else:
                st.success("✅ Meta description length is optimal (50-160 characters)")
        
        # TAB 2: Headings
        with tab2:
            st.subheader("Heading Structure")
            
            headings_df = pd.DataFrame(
                list(results['Headings'].items()),
                columns=["Heading Tag", "Count"]
            )
            st.dataframe(headings_df, use_container_width=True, hide_index=True)
            
            st.subheader("Recommendations")
            if results['Headings']['h1'] == 0:
                st.error("❌ No H1 heading found! Add one main H1 heading")
            elif results['Headings']['h1'] > 1:
                st.warning("⚠️ Multiple H1 headings found. Use only one H1")
            else:
                st.success("✅ Good! Exactly one H1 heading")
            
            if results['Headings']['h2'] == 0:
                st.warning("⚠️ No H2 headings found. Use H2 for main sections")
        
        # TAB 3: Images
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Images", results['Total_Images'])
                st.metric("Images with Alt Text", results['Images_With_Alt'])
            
            with col2:
                st.metric("Images without Alt Text", results['Images_Without_Alt'])
                if results['Total_Images'] > 0:
                    alt_percentage = (results['Images_With_Alt'] / results['Total_Images']) * 100
                    st.metric("Alt Text Coverage", f"{alt_percentage:.1f}%")
            
            if results['Images_Without_Alt'] > 0:
                st.error(f"❌ {results['Images_Without_Alt']} images missing alt text")
                st.info("Add descriptive alt text for better accessibility and SEO")
            else:
                st.success("✅ All images have alt text!")
        
        # TAB 4: Links
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("🔗 Internal Links", results['Internal_Links_Count'])
                st.caption("Links to same website")
            
            with col2:
                st.metric("🌐 External Links", results['External_Links_Count'])
                st.caption("Links to other websites")
            
            if results['Internal_Links_Count'] == 0:
                st.warning("⚠️ No internal links found")
            
            if results['External_Links_Count'] == 0:
                st.info("💡 Consider adding external links to authoritative sources")
        
        # SEO Score Gauge Chart
        st.markdown("---")
        st.subheader("📈 SEO Score Visualization")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=results['SEO_Score'],
            title={'text': "Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 50], 'color': "#ff6b6b"},
                    {'range': [50, 70], 'color': "#ffd93d"},
                    {'range': [70, 100], 'color': "#6bcf7f"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Actionable Recommendations
        st.markdown("---")
        st.subheader("🎯 Actionable Recommendations")
        
        recommendations = []
        
        if results['Title_Length'] < 30 or results['Title_Length'] > 60:
            recommendations.append("• Optimize title length to 30-60 characters")
        
        if results['Meta_Description_Length'] < 50 or results['Meta_Description_Length'] > 160:
            recommendations.append("• Adjust meta description to 50-160 characters")
        
        if results['Headings']['h1'] != 1:
            recommendations.append("• Use exactly one H1 heading per page")
        
        if results['Images_Without_Alt'] > 0:
            recommendations.append(f"• Add alt text to {results['Images_Without_Alt']} images")
        
        if results['Internal_Links_Count'] < 3:
            recommendations.append("• Add more internal links to improve site structure")
        
        if recommendations:
            for rec in recommendations:
                st.write(rec)
        else:
            st.success("🎉 Excellent! Your page follows SEO best practices!")
        
        # Raw data expander
        with st.expander("🔧 View Raw Analysis Data"):
            st.json(results)

elif analyze_button and not url_input:
    st.warning("⚠️ Please enter a URL to analyze")

else:
    # Welcome message
    st.info("👈 Enter a URL in the box above and click 'Analyze URL' to get started!")
    
    # Feature preview
    with st.expander("🌟 Features of this SEO Tool"):
        st.markdown("""
        **This tool analyzes:**
        
        ✅ **Page Title** - Length and presence check
        ✅ **Meta Description** - Length optimization
        ✅ **Heading Structure** - H1 to H6 usage
        ✅ **Images** - Alt text coverage
        ✅ **Links** - Internal vs external distribution
        ✅ **SEO Score** - Overall score out of 100
        
        **Try it with your own website or test with example URLs!**
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with Streamlit | SEO Analysis Tool"
    "</div>",
    unsafe_allow_html=True
)
