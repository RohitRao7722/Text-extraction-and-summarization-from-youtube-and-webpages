                 
                
    
import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi

# Streamlit app configuration
st.set_page_config(page_title="Langchain: Summarize Text from YouTube or Website", page_icon="😊")
st.title("😊 Langchain: Summarize Text from YouTube or Website")
st.subheader("Summarize URL")

# Get GROQ API key from the user and URL to be summarized
with st.sidebar:
    groq_api_key = st.text_input("GROQ API Key", value="", type="password")

generic_url = st.text_input("Enter URL here", label_visibility="collapsed")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma-7b-It")

prompt_template = """
Provide a summary of the following content in 300 words:
Content: {text}
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

if st.button("Summarize Content from YouTube or Website"):
    # Validate all inputs
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide the necessary information to get started.")
    elif not validators.url(generic_url):
        st.error("Please provide a valid URL. It can be a YouTube video or website URL.")
    else:
        try:
            with st.spinner("Loading..."):
                # Loading data from YouTube or website
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    try:
                        loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=True)
                        docs = loader.load()
                    except Exception as e:
                        st.warning("Failed to retrieve data using PyTube. Trying to get the video transcript.")
                        try:
                            video_id = generic_url.split("v=")[-1]
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            transcript_text = " ".join([entry['text'] for entry in transcript])
                            docs = [transcript_text]
                        except Exception as transcript_error:
                            st.error(f"Could not extract video transcript. Error: {transcript_error}")
                            docs = None
                else:
                    loader = UnstructuredURLLoader(urls=[generic_url], ssl_verify=False,
                                                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                    docs = loader.load()
                
                # Chain for summarization
                if docs:
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    output_summary = chain.run(docs)
                    st.success(output_summary)
                else:
                    st.error("No content found to summarize.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
