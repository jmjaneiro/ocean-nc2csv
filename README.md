# 🌊 OceanNC to CSV Converter

> Ferramenta interativa desenhada para estudantes de **Oceanografia Física e Biologia Marinha** para converter ficheiros NetCDF (`.nc`) em tabelas CSV prontas para Excel, R ou QGIS, com um assistente inteligente de dimensões (4D/3D).

---

## 🎯 Porquê esta ferramenta?

Os dados oceanográficos (Copernicus Marine, NOAA, modelos ROMS/NEMO, satélites) vêm em formato **NetCDF multidimensional** (Tempo, Profundidade, Latitude, Longitude).

Para alunos de Biologia Marinha que necessitam de trabalhar em Excel ou R, surgem dois grandes problemas:
1. **O limite do Microsoft Excel**: O Excel suporta no máximo **1.048.576 linhas**. Uma grelha 4D completa pode facilmente atingir dezenas de milhões de pontos.
2. **Máscara de Terra**: Grelhas de modelos cobrem tanto o mar como a terra. Em terra, os valores são nulos (`NaN` ou `-9999`). Exportar estes pontos cria ficheiros enormes e corrompe cálculos estatísticos simples.

### O que o Assistente Inteligente faz:
* 🔍 **Analisa as dimensões automaticamente**: Identifica se o ficheiro é 2D, 3D ou 4D.
* ⚠️ **Alerta de tamanho em tempo real**: Calcula os pontos teóricos e avisa se o ficheiro cabe no Excel.
* 🌊 **Fatia de Profundidade intuitiva**: Permite escolher apenas a **Superfície (0 m)** com um clique ou selecionar um nível específico.
* ⏱️ **Filtro Temporal**: Permite extrair todos os passos ou isolar uma data de amostragem.
* 📍 **Recorte Geográfico (Bounding Box)**: Permite focar na área de estudo (ex: Costa de Portugal ou Ria Formosa).
* 🧹 **Limpeza Automática**: Exclui pontos em terra para tornar o CSV leve.
* 🇵🇹 **Compatibilidade com Excel PT**: Permite escolher separador de ponto e vírgula (`;`) e vírgula decimal (`,`) para abrir diretamente no Excel em português com 2 cliques.

---

## 🚀 Como Colocar Online Gratuitamente (GitHub + Streamlit Cloud)

Para partilhar um link direto com os alunos sem que eles precisem de instalar nada:

### Passo 1: Criar o Repositório no GitHub
1. Crie um novo repositório no seu GitHub (ex: `ocean-nc2csv`).
2. Envie os ficheiros desta pasta para o repositório:
   ```bash
   git init
   git add .
   git commit -m "Versão inicial da app OceanNC to CSV"
   git branch -M main
   git remote add origin https://github.com/SEU_UTILIZADOR/ocean-nc2csv.git
   git push -u origin main
   ```

### Passo 2: Publicar no Streamlit Community Cloud (Grátis)
1. Aceda a [share.streamlit.io](https://share.streamlit.io) e faça login com o GitHub.
2. Clique em **"New app"**.
3. Selecione o repositório `ocean-nc2csv`, ramo `main` e ficheiro principal `app.py`.
4. Clique em **"Deploy"**!
5. Em menos de 2 minutos terá um link público (ex: `https://ocean-nc2csv.streamlit.app`) para partilhar com os alunos.

---

## 💻 Como Executar Localmente no Computador

Se quiser testar ou correr a aplicação no seu computador:

```bash
# 1. Entrar na pasta do projeto
cd ocean-nc2csv

# 2. Ativar o ambiente virtual (se criado) ou instalar dependências
pip install -r requirements.txt

# 3. Gerar ficheiro de exemplo (opcional)
python generate_sample_nc.py

# 4. Iniciar a aplicação no browser
streamlit run app.py
```

A app abrirá automaticamente no browser no endereço `http://localhost:8501`.
