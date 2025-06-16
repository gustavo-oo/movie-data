from graphviz import Digraph

# Criando o diagrama com qualidade superior e mais espaçado
dot = Digraph("Data_Transformation_Pipeline", format="png")

# Ajustando layout e espaçamento para melhor organização e maior altura
dot.attr(dpi="100", rankdir="LR", nodesep="1.2", ranksep="1", size="30", ratio="expand")

# Definição dos nós principais (losangos e quadrados em linha reta)
dot.node("RAW", "Dados Brutos (CSV do TMDb)", shape="parallelogram", style="filled", fillcolor="lightgrey", fontsize="60")
dot.node("MAP", "Mapeamento e Transformação", shape="box", style="filled", fillcolor="lightblue", fontsize="60")
dot.node("REMOVE", "Remoção de Colunas Irrelevantes", shape="box", style="filled", fillcolor="lightcoral", fontsize="60")
dot.node("FILTER", "Aplicação de Filtros", shape="box", style="filled", fillcolor="lightgreen", fontsize="60")
dot.node("FINAL", "Dados Tratados e Prontos para Análise", shape="parallelogram", style="filled", fillcolor="gold", fontsize="60")

# Agrupamento dos subprocessos abaixo dos retângulos principais
with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("MAP_GENRE", "Mapeamento de Gêneros\n(ID → Nome)", shape="ellipse", fontsize="55")
    s.node("MAP_KEYWORDS", "Mapeamento de Palavras-chave\n(Dicionário → Nome)", shape="ellipse", fontsize="55")
    s.node("MAP_LANG", "Mapeamento de Idiomas\n(ID → Nome)", shape="ellipse", fontsize="55")
    s.node("MAP_COUNTRY", "Mapeamento de Países\n(ISO → Nome)", shape="ellipse", fontsize="55")
    s.node("MAP_COMPANIES", "Mapeamento de Empresas de Produção\n(Extração Nome + País)", shape="ellipse", fontsize="55")
    s.node("MAP_CAST_CREW", "Mapeamento de Gênero de Elenco e Equipe\n(ID → Nome)", shape="ellipse", fontsize="55")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("REMOVE_EXTERNAL", "Remoção de Referências Externas\n(Imagens, Vídeos, Homepage)", shape="ellipse", fontsize="55")
    s.node("REMOVE_GENRE", "Remoção de Identificadores Redundantes\n(genre_ids → genres)", shape="ellipse", fontsize="55")
    s.node("REMOVE_UNUSED", "Remoção de Colunas Não Utilizadas\n(IMDb ID, Tagline, Status, Popularidade)", shape="ellipse", fontsize="55")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("FILTER_GENERAL", "Seleção Geral\n(Remove NaN e Valores Zero)", shape="ellipse", fontsize="55")
    s.node("FILTER_BRA_EUA", "Filtro Brasil x EUA\n(Permite NaN em Receita e Orçamento)", shape="ellipse", fontsize="55")

# Conectando os nós principais em linha reta (fluxo principal destacado)
dot.edge("RAW", "MAP", penwidth="7")
dot.edge("MAP", "REMOVE", penwidth="7")
dot.edge("REMOVE", "FILTER", penwidth="7")
dot.edge("FILTER", "FINAL", penwidth="7")

# Conectando subprocessos ao mapeamento (penwidth aumentado)
dot.edge("MAP", "MAP_GENRE", style="dashed", penwidth="5")
dot.edge("MAP", "MAP_KEYWORDS", style="dashed", penwidth="5")
dot.edge("MAP", "MAP_LANG", style="dashed", penwidth="5")
dot.edge("MAP", "MAP_COUNTRY", style="dashed", penwidth="5")
dot.edge("MAP", "MAP_COMPANIES", style="dashed", penwidth="5")
dot.edge("MAP", "MAP_CAST_CREW", style="dashed", penwidth="5")

# Conectando subprocessos à remoção de colunas (penwidth aumentado)
dot.edge("REMOVE", "REMOVE_EXTERNAL", style="dashed", penwidth="5")
dot.edge("REMOVE", "REMOVE_GENRE", style="dashed", penwidth="5")
dot.edge("REMOVE", "REMOVE_UNUSED", style="dashed", penwidth="5")

# Conectando subprocessos aos filtros aplicados (penwidth aumentado)
dot.edge("FILTER", "FILTER_GENERAL", style="dashed", penwidth="5")
dot.edge("FILTER", "FILTER_BRA_EUA", style="dashed", penwidth="5")

# Gerando e salvando o diagrama com alta qualidade
dot.render("data_transformation_pipeline", format="png")
dot.render("data_transformation_pipeline", format="pdf")

print("Diagrama gerado com sucesso: 'data_transformation_pipeline.png' e 'data_transformation_pipeline.pdf'")
