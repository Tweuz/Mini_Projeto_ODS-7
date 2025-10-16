import streamlit as st # Biblioteca principal para criar o web app
import pandas as pd # Para manipulação e análise de dados (DataFrames)
import plotly.express as px # Para criar gráficos interativos

# --- 1. Estilização Personalizada (CSS) ---
# Aqui, definimos estilos para dar uma cara única ao nosso dashboard.
st.markdown("""
    <style>
    /* Estiliza o sidebar (barra lateral) */
    [data-testid="stSidebar"] {
        background-color: #FDB713; /* Amarelo Vibrante, inspirado no ODS 7 (Energia Limpa) */
        padding: 2rem 1rem; /* Espaçamento interno */
        color: white; /* Cor do texto no sidebar */
    }

    /* Estiliza o texto dentro do multiselect no sidebar */
    [data-testid="stSidebar"] .stMultiSelect [data-testid="stMarkdownContainer"] p {
        background-color: #FDB713;
        color: #ffffff;
        border-radius: 5px;
        padding: 2px 6px;
        margin: 2px;
    }
    </style>
""", unsafe_allow_html=True) # Permite a injeção de HTML/CSS

# --- 2. Configuração Inicial da Página ---
# Define como a página será exibida.
st.set_page_config(
    page_title="Dashboard ODS 7", # Título que aparece na aba do navegador
    layout="wide" # Usa a largura total da tela para o conteúdo
)

# --- 3. Carregamento e Preparação dos Dados ---
# Usamos o decorator st.cache_data para que o Streamlit carregue o arquivo
# apenas uma vez, tornando o app mais rápido!
@st.cache_data
def carregar_dados():
    # 💡 Dica: Certifique-se de que 'acesso_eletricidade_limpo.csv' está na mesma pasta!
    df = pd.read_csv('acesso_eletricidade_limpo.csv')
    # Renomeamos a coluna 'Pais' para 'Entidade' para ser mais genérico e claro
    df = df.rename(columns={'Pais': 'Entidade'})
    return df

df = carregar_dados() # Carrega o DataFrame

# --- 4. Título Principal ---
st.title("Acessibilidade à Eletricidade")

# --- 5. Sidebar (Barra Lateral para Filtros) ---
# A barra lateral é onde colocamos os controles para interagir com os dados.
try:
    # Tenta carregar uma imagem (logotipo, por exemplo)
    st.sidebar.image('images.png')
except:
    # Se a imagem não for encontrada, mostra um aviso
    st.sidebar.warning("Imagem 'images.png' não encontrada.")

st.sidebar.header("Filtros")

# Prepara as listas de opções para os filtros
lista_entidades = sorted(df['Entidade'].unique())
lista_anos = sorted(df['Ano'].unique())

# Filtro MultiSelect: Permite escolher quais países/entidades visualizar
entidades_selecionados = st.sidebar.multiselect(
    label="Escolha as entidades para visualizar:",
    options=lista_entidades,
    # Define uma seleção padrão para facilitar o primeiro acesso
    default=['Brazil', 'Angola', 'South Africa', 'United States', 'India']
)

# --- 6. Filtragem dos Dados ---
# Aplica o filtro selecionado pelo usuário no DataFrame original
df_filtrado = df[df['Entidade'].isin(entidades_selecionados)]

# --- 7. Criação das Abas de Visualização ---
# Organizamos o dashboard em abas para separar os tipos de gráficos.
tab1, tab2, tab3 = st.tabs(["Evolução", "Média por Entidade", "Foco em um Ano"])

# --- 8. Visualizações em Plotly ---

# --- Aba 1: Evolução (Gráfico de Linhas) ---
with tab1:
    st.subheader("Evolução do Acesso à Eletricidade")
    # Gráfico de linha: Ótimo para ver a tendência ao longo do tempo (Ano)
    fig1 = px.line(
        df_filtrado,
        x='Ano',
        y='Percentual_Acesso',
        color='Entidade', # Uma linha diferente para cada entidade
        markers=True, # Adiciona pontos para destacar os anos
        title='Evolução do Acesso à Eletricidade nas Entidades Selecionados',
        labels={'Percentual_Acesso': '% da População com Acesso'}
    )
    st.plotly_chart(fig1, use_container_width=True) # Exibe o gráfico

# --- Aba 2: Média por Entidade (Gráfico de Barras) ---
with tab2:
    st.subheader("Média do Percentual de Acesso à Eletricidade (2000–2023)")

    # 1. Calcula a média de acesso para cada entidade selecionada
    df_media = (
        df_filtrado.groupby('Entidade')['Percentual_Acesso']
        .mean()
        .reset_index()
        # Ordena para ter uma visualização mais organizada no gráfico de barras
        .sort_values(by='Percentual_Acesso', ascending=True)
    )

    # 2. Cria o Gráfico de Barras
    fig2 = px.bar(
        df_media,
        x='Percentual_Acesso',
        y='Entidade',
        orientation='h', # 'h' para horizontal (melhor para rótulos longos)
        color='Entidade',
        title='Média do Acesso à Eletricidade por País',
        labels={'Percentual_Acesso': 'Média % da População com Acesso', 'Entidade': 'Entidade'}
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Aba 3: Foco em um Ano (Gráfico de Tiras/Strip Plot) ---
with tab3:
    st.subheader("Comparativo de Acesso à Eletricidade em um Ano Específico")
    # Seletor para escolher o ano (começa no ano mais recente)
    ano_foco = st.selectbox(
        "Escolha o ano de foco:",
        lista_anos,
        index=len(lista_anos)-1 # O 'index=-1' seleciona o último item da lista (ano mais recente)
    )

    # 1. Filtra o DataFrame apenas para o ano escolhido
    df_ano = df[df['Ano'] == ano_foco].copy()
    # 2. Filtra pelas entidades selecionadas no sidebar
    df_ano = df_ano[df_ano['Entidade'].isin(entidades_selecionados)]
    # Adiciona uma coluna de texto formatado para usar no hover/rótulos (apesar de não usado no gráfico final, é uma boa prática)
    df_ano['Percentual_Acesso_Texto'] = df_ano['Percentual_Acesso'].apply(lambda x: f'{x:.1f}%')


    # 3. Cria o Strip Plot
    # Strip Plot: Útil para mostrar a distribuição de um valor numérico por categoria.
    # Como só teremos um ponto por entidade neste caso (um único ano), funciona
    # como um gráfico de pontos de comparação.
    fig3 = px.strip(
        df_ano,
        x='Percentual_Acesso',
        y='Entidade',
        orientation='h',
        color='Entidade',
        hover_name='Entidade',
        # Configura o que aparece ao passar o mouse (hover)
        hover_data={'Percentual_Acesso': ':.2f', 'Entidade': False},
        title=f'Comparativo de Acesso à Eletricidade em {ano_foco}',
        labels={'Percentual_Acesso': '% da População com Acesso', 'Entidade': 'Entidade'}
    )
    # Ajusta o visual: aumenta o tamanho dos pontos para melhor visibilidade
    fig3.update_traces(marker=dict(size=15))
    st.plotly_chart(fig3, use_container_width=True)

# --- 9. Visualização Opcional dos Dados ---
# Um 'Expander' é um widget que pode ser aberto e fechado, economizando espaço.
with st.expander("Ver dados filtrados"):
    st.dataframe(df_filtrado) # Mostra o DataFrame que está sendo usado nos gráficos