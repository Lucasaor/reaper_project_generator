import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

def main():
    st.title("Black Violet - Gerador de Setlists no Reaper")
    st.write("Esta é uma aplicação simples para o gerar setlists baseado em projetos do REAPER.")
    
    file = st.file_uploader("Carregar um arquivo .rpp")
    if "song_list" not in st.session_state:
        st.session_state.song_list = []
    if "setlist" not in st.session_state:
        st.session_state.setlist = []
    setlist_ok = False
    
    if st.button("Carregar arquivo"):
        if file:
            if file.name.endswith(".rpp") or file.name.endswith(".RPP"):
                with st.spinner(text="Carregando projeto..."):
                    response = requests.post(f"{API_BASE_URL}/load_project", files={"file": file})
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error(response.json()["error"])
                    file.seek(0)
                    file.truncate(0)
        else:
                st.error("Tipo de arquivo inválido. Por favor, carregue um arquivo .rpp.")

    if st.button("Obter lista de músicas"):
        response = requests.get(f"{API_BASE_URL}/get_song_list")
        st.session_state.song_list = response.json()
        st.success("Lista de músicas obtida com sucesso!")
    
    
    st.session_state.setlist = st.multiselect("Selecione as músicas para o setlist aqui", st.session_state.song_list, default=None)

    
    if st.button("Gerar novo rpp com setlist"):
        st.spinner(text="Definindo setlist...")
        print(st.session_state.setlist)
       
        response = requests.post(f"{API_BASE_URL}/set_setlist", json=st.session_state.setlist)
        st.success(response.json()["message"])
        
    
        st.spinner(text="Exportando projeto RPP...")
        response = requests.get(f"{API_BASE_URL}/export_rpp_project")
        if response.status_code == 200:
            content_disposition = response.headers.get("content-disposition")
            if content_disposition:
                filename = content_disposition.split("filename=")[-1].strip('"')
                filename = filename.replace('attachment; filename=', '').replace('utf-8\"', '')
                st.download_button(
                    label="Baixar projeto exportado",
                    data=response.content,
                    file_name=filename,
                    mime="application/octet-stream"
                )
            else:
                st.error("Nome do arquivo não encontrado nos cabeçalhos da resposta.")
        else:
            st.error("Falha ao exportar projeto.")


if __name__ == '__main__':
    main()