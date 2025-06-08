import streamlit as st
import pandas as pd
import numpy as np
from utils.constants import DataConfig, MarkConfig
import plotly.express as px
import plotly.graph_objects as go


def show_classroom_table(data:pd.DataFrame, title:str=None):
    with st.expander(f"Tabla global clase ({title})"):
        st.dataframe(data, use_container_width=True)


def subject_visualization(data:pd.DataFrame, selected_subject:str, title:str):

    # Count the occurrences of each unique value in the selected column
    value_counts = data[selected_subject].value_counts()
    # Create a pie chart using Plotly with custom colors
    figGlobal = px.pie(
        value_counts, 
        names=value_counts.index, 
        values=value_counts.values, 
        title=title,
        color=value_counts.index,  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figGlobal)


def student_mark_freq_visualization(data:pd.DataFrame, std_name:str, title:str):
    # Display pie chart of marks count
    count_cols = [f"{x}_COUNT" for x in MarkConfig.LIST.value]
    student_data_count = data[data["NOM"] == std_name][count_cols].iloc[0]

    # Prepare data for Plotly
    plot_data = pd.DataFrame({
        'Nota': [label.replace('_COUNT', '') for label in count_cols],
        'Frecuencia': student_data_count.values
    })

    # Create interactive pie chart
    fig = px.pie(
        plot_data,
        values='Frecuencia',
        names='Nota',
        title=title,
        color='Nota',  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value,
        hover_data=['Frecuencia'],
        # labels={'Frecuencia': 'Cantidad'}
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def student_marks_per_subject(data:pd.DataFrame, std_name:str, title:str):
    student_data = data[data["NOM"] == std_name]
    student_data = student_data[list(DataConfig.SUBJ_NAMES.value)]
    
    # Display bar diagram from selected student
    fig = go.Figure()
    # Preparar datos para Plotly
    columns = list(DataConfig.SUBJ_NAMES.value)
    values = list(student_data.iloc[0])
    colors = [MarkConfig.COLOR_MAP.value[val] for val in values]
    heights = [MarkConfig.HEIGHT_MAP.value[val] for val in values]
    
    # Set bar diagram content
    fig.add_trace(go.Bar(
        x=columns,
        y=heights,  # Usar alturas variables
        marker_color=colors,
        text=values,
        textposition='inside',
        textfont=dict(color='white', size=14),
        hoverinfo='text',
        hovertext=[f"Columna: {col}<br>Valor: {val}" for col, val in zip(columns, values)]
    ))

    # Personalizar diseño
    fig.update_layout(
        title=title,
        yaxis=dict(showticklabels=False, range=[0, 1.1]),
        height=300,
        showlegend=False,
        hovermode='closest',
        yaxis_autorange=True
    )
    
    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)


def show_student_evolution(data1:pd.DataFrame, data2:pd.DataFrame, student_name:str, title:str):
    """Muestra la evolución de las notas de un alumno específico entre trimestres.
    
    Args:
        data1 (pd.DataFrame): Datos del primer trimestre
        data2 (pd.DataFrame): Datos del segundo trimestre
        student_name (str): Nombre del alumno
        title (str): Título de la visualización
    """
    # Obtener las notas del primer trimestre
    t1_marks = data1[data1["NOM"] == student_name][list(DataConfig.SUBJ_NAMES.value)]
    t1_marks = t1_marks.replace(MarkConfig.HEIGHT_MAP.value)
    t1_avg = t1_marks.mean().mean()
    
    # Obtener las notas del segundo trimestre
    t2_marks = data2[data2["NOM"] == student_name][list(DataConfig.SUBJ_NAMES.value)]
    t2_marks = t2_marks.replace(MarkConfig.HEIGHT_MAP.value)
    t2_avg = t2_marks.mean().mean()
    
    # Crear DataFrame con la evolución por asignatura
    evolution_data = []
    for subject in DataConfig.SUBJ_NAMES.value:
        t1_subj = t1_marks[subject].iloc[0]
        t2_subj = t2_marks[subject].iloc[0]
        evolution_data.append({
            "Asignatura": DataConfig.get_key_from_value(subject),
            "Trimestre 1": t1_subj,
            "Trimestre 2": t2_subj,
            "Evolución": t2_subj - t1_subj
        })
    
    evolution_df = pd.DataFrame(evolution_data)
    
    # Crear el gráfico de dispersión con líneas
    fig = go.Figure()
    
    # Añadir puntos y líneas para cada asignatura
    for _, row in evolution_df.iterrows():
        color = "red" if row["Evolución"] < 0 else "green" if row["Evolución"] > 0 else "gray"
        fig.add_trace(go.Scatter(
            x=["Trimestre 1", "Trimestre 2"],
            y=[row["Trimestre 1"], row["Trimestre 2"]],
            mode='lines+markers',
            name=row["Asignatura"],
            line=dict(color=color),
            text=[f"{row['Asignatura']}<br>Nota: {MarkConfig.get_mark_from_height(y)}" for y in [row["Trimestre 1"], row["Trimestre 2"]]],
            hoverinfo='text'
        ))
    
    # Personalizar el diseño
    fig.update_layout(
        title=title,
        xaxis_title="Trimestre",
        yaxis_title="Nota",
        yaxis=dict(
            range=[0, 4.5],  # Rango basado en HEIGHT_MAP
            ticktext=["NA", "AS", "AN", "AE"],
            tickvals=[1, 2, 3, 4]
        ),
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla con la evolución
    st.subheader("Resumen de Evolución por Asignatura")
    # Convertir los valores numéricos a notas en la tabla
    display_df = evolution_df.copy()
    display_df["Trimestre 1"] = display_df["Trimestre 1"].apply(lambda x: MarkConfig.get_mark_from_height(x))
    display_df["Trimestre 2"] = display_df["Trimestre 2"].apply(lambda x: MarkConfig.get_mark_from_height(x))
    st.dataframe(
        display_df.sort_values("Evolución", ascending=False),
        use_container_width=True
    )
    
    # Mostrar resumen general
    st.subheader("Resumen General")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio T1", MarkConfig.get_mark_from_height(t1_avg))
    with col2:
        st.metric("Promedio T2", MarkConfig.get_mark_from_height(t2_avg))
    with col3:
        st.metric("Evolución", f"{t2_avg - t1_avg:+.2f}", delta=f"{t2_avg - t1_avg:+.2f}")


def display_marks_pie_chart(student_data):
    """Display a pie chart of the student's marks by qualification level"""
    # Initialize counters for each qualification level
    qualification_counts = {
        "": 0,
        MarkConfig.NA.value: 0,
        MarkConfig.AS.value: 0,
        MarkConfig.AN.value: 0,
        MarkConfig.AE.value: 0
    }

    # Count subjects by qualification level
    for materia in student_data['materies']:
        qualificacio = materia['qualificacio']
        if qualificacio == MarkConfig.NA.value:
            qualification_counts[MarkConfig.NA.value] += 1
        elif qualificacio == MarkConfig.AS.value:
            qualification_counts[MarkConfig.AS.value] += 1
        elif qualificacio == MarkConfig.AN.value:
            qualification_counts[MarkConfig.AN.value] += 1
        elif qualificacio == MarkConfig.AE.value:
            qualification_counts[MarkConfig.AE.value] += 1
        else:
            qualification_counts[""] += 1

    # Filter out empty values
    filtered_counts = {k: v for k, v in qualification_counts.items() if k != "" and v > 0}

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(filtered_counts.keys()),
        values=list(filtered_counts.values()),
        hole=.3,  # Creates a donut chart
        textinfo='label+percent+value',
        insidetextorientation='radial',
        marker_colors=[MarkConfig.COLOR_MAP.value[mark] for mark in filtered_counts.keys()]
    )])

    # Update layout
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)  # Add margins on all sides
    )

    st.subheader("Distribució de Qualificacions")
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def display_group_statistics(students):
    """Display statistics for the entire group"""
    # Initialize counters for each qualification level
    qualification_counts = {
        MarkConfig.NA.value: 0,
        MarkConfig.AS.value: 0,
        MarkConfig.AN.value: 0,
        MarkConfig.AE.value: 0
    }

    # Count all marks across all students and subjects
    for student in students:
        for materia in student['materies']:
            qualificacio = materia['qualificacio']
            if qualificacio in qualification_counts:
                qualification_counts[qualificacio] += 1

    # Filter out empty values
    filtered_counts = {k: v for k, v in qualification_counts.items() if v > 0}

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(filtered_counts.keys()),
        values=list(filtered_counts.values()),
        hole=.3,  # Creates a donut chart
        textinfo='label+percent+value',
        insidetextorientation='radial',
        marker_colors=[MarkConfig.COLOR_MAP.value[mark] for mark in filtered_counts.keys()]
    )])

    # Update layout
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)  # Add margins on all sides
    )

    st.subheader("Distribució de qualificacions per trimestre")
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def group_failure_table(students):
    categories = {
        "Tot aprovat": [],
        "Fins a 3 susp.": [],
        "4 o 5 susp.": [],
        "Més de 5 susp.": []
    }
    for student in students:
        n_susp = sum(1 for m in student['materies'] if m['qualificacio'] == MarkConfig.NA.value)
        name = student['nom_cognoms']
        if n_susp == 0:
            categories["Tot aprovat"].append(name)
        elif 1 <= n_susp <= 3:
            categories["Fins a 3 susp."].append(name)
        elif 4 <= n_susp <= 5:
            categories["4 o 5 susp."].append(name)
        else:
            categories["Més de 5 susp."].append(name)
    total = len(students)
    data = []
    for cat, names in categories.items():
        data.append({
            "Categoria": cat,
            "Nº d'alumnes": len(names),
            "%": f"{(len(names)/total*100):.1f}%",
            "Alumnes": '; '.join(names)
        })
    st.subheader("Resum de suspensos per alumne")
    st.dataframe(data, hide_index=True)
    
    # Pie chart for categories
    labels = [row["Categoria"] for row in data]
    values = [row["Nº d'alumnes"] for row in data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        textinfo='label+percent+value',
        insidetextorientation='radial',
        marker_colors=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"]
    )])
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.subheader("Distribució d'alumnes per categoria (Diagrama de sectors)")
    st.plotly_chart(fig, use_container_width=True)


def display_subjects_bar_chart(students):
    st.subheader("Distribució de qualificacions per assignatura")

    # Add course level checkboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        first_year = st.checkbox("1r", value=False, key="bar_1r")
    with col2:
        second_year = st.checkbox("2n", value=False, key="bar_2n")
    with col3:
        third_year = st.checkbox("3r", value=True, key="bar_3r")

    selected_courses = []
    if first_year:
        selected_courses.append("1r")
    if second_year:
        selected_courses.append("2n")
    if third_year:
        selected_courses.append("3r")

    # Obtener todas las materias filtradas por curso
    all_subjects = set()
    for student in students:
        for m in student['materies']:
            if any(c in m['materia'] for c in selected_courses):
                all_subjects.add(m['materia'])
    all_subjects = sorted(list(all_subjects))

    # Contar NA, AS, AN, AE por materia
    data = []
    for subject in all_subjects:
        counts = {k: 0 for k in [MarkConfig.NA.value, MarkConfig.AS.value, MarkConfig.AN.value, MarkConfig.AE.value]}
        for student in students:
            for m in student['materies']:
                if m['materia'] == subject and any(c in m['materia'] for c in selected_courses):
                    if m['qualificacio'] in counts:
                        counts[m['qualificacio']] += 1
        for mark, count in counts.items():
            data.append({"Assignatura": subject, "Qualificació": mark, "Comptador": count})

    df = pd.DataFrame(data)
    if not df.empty:
        fig = px.bar(
            df,
            x="Assignatura",
            y="Comptador",
            color="Qualificació",
            barmode="group",
            color_discrete_map=MarkConfig.COLOR_MAP.value
        )
        fig.update_layout(height=500, xaxis_title="Assignatura", yaxis_title="Nombre d'alumnes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecciona almenys un curs per veure el gràfic.")


def display_student_ranking(students):
    st.subheader("Ranking d'alumnes per mitjana numèrica (NA=2.5, AS=5, AN=7.5, AE=10)")
    mark_to_value = {
        "No assoliment": 2.5,
        "Assoliment satisfactori": 5,
        "Assoliment notable": 7.5,
        "Assoliment excel·lent": 10
    }
    ranking = []
    for student in students:
        values = [
            mark_to_value[m['qualificacio']]
            for m in student['materies']
            if m['qualificacio'] in mark_to_value
        ]
        if values:
            avg = sum(values) / len(values)
            avg_10 = float(f"{avg:.2g}")
        else:
            avg_10 = "N/A"
        ranking.append({
            "Alumne": student['nom_cognoms'],
            "Mitjana (0-10)": avg_10
        })
    # Ordenar de mayor a menor media
    ranking = sorted(ranking, key=lambda x: (x["Mitjana (0-10)"] if x["Mitjana (0-10)"] != "N/A" else -1), reverse=True)
    df = pd.DataFrame(ranking)
    def highlight_top_bottom(col):
        colors = [''] * len(col)
        # Solo filas con valor numérico
        numeric_idx = [i for i, v in enumerate(col) if isinstance(v, (int, float))]
        # Top 5 verde oscuro con texto negro
        for i in numeric_idx[:5]:
            colors[i] = 'background-color: #218739; color: black'  # verde oscuro
        # Bottom 5 rojo claro con texto negro
        for i in numeric_idx[-5:]:
            colors[i] = 'background-color: #ffb3b3; color: black'
        return colors
    styled_df = df.style.apply(highlight_top_bottom, subset=['Mitjana (0-10)'])
    st.dataframe(styled_df, hide_index=True, use_container_width=True)


def display_student_subject_heatmap(students):
    """Display a heatmap of students vs subjects showing marks distribution"""
    st.subheader("Mapa de calor: Alumnes vs. Assignatures")
    
    # Add course level checkboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        first_year = st.checkbox("1r", value=False, key="heatmap_1r")
    with col2:
        second_year = st.checkbox("2n", value=False, key="heatmap_2n")
    with col3:
        third_year = st.checkbox("3r", value=True, key="heatmap_3r")

    selected_courses = []
    if first_year:
        selected_courses.append("1r")
    if second_year:
        selected_courses.append("2n")
    if third_year:
        selected_courses.append("3r")

    # Get all subjects for selected courses
    all_subjects = set()
    for student in students:
        for m in student['materies']:
            if any(c in m['materia'] for c in selected_courses):
                all_subjects.add(m['materia'])
    all_subjects = sorted(list(all_subjects))

    # Create matrix of marks
    matrix_data = []
    for student in students:
        row = {'Alumne': student['nom_cognoms']}
        for subject in all_subjects:
            # Find the mark for this subject
            mark = next((m['qualificacio'] for m in student['materies'] if m['materia'] == subject), None)
            if mark:
                # Convert mark to numeric value for heatmap
                if mark == MarkConfig.NA.value:
                    row[subject] = 0
                elif mark == MarkConfig.AS.value:
                    row[subject] = 1
                elif mark == MarkConfig.AN.value:
                    row[subject] = 2
                elif mark == MarkConfig.AE.value:
                    row[subject] = 3
                else:
                    row[subject] = None
            else:
                row[subject] = None
        matrix_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(matrix_data)
    df = df.set_index('Alumne')

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=[
            [0, MarkConfig.COLOR_MAP.value[MarkConfig.NA.value]],  # NA
            [0.33, MarkConfig.COLOR_MAP.value[MarkConfig.AS.value]],  # AS
            [0.66, MarkConfig.COLOR_MAP.value[MarkConfig.AN.value]],  # AN
            [1, MarkConfig.COLOR_MAP.value[MarkConfig.AE.value]]  # AE
        ],
        colorbar=dict(
            title="Qualificació",
            ticktext=["NA", "AS", "AN", "AE"],
            tickvals=[0, 1, 2, 3]
        ),
        hoverongaps=False,
        hoverinfo='text',
        text=[[f"{MarkConfig.get_mark_from_height(val)}" if val is not None else "N/A" for val in row] for row in df.values]
    ))

    # Update layout
    fig.update_layout(
        height=max(400, len(students) * 25),  # Adjust height based on number of students
        xaxis_title="Assignatures",
        yaxis_title="Alumnes",
        xaxis={'tickangle': 45},
        margin=dict(t=50, b=100, l=100, r=50)  # Add margins for labels
    )

    # Display the heatmap
    st.plotly_chart(fig, use_container_width=True)