import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from utils.constants import MarkConfig
from utils.data_normalizer import normalize_student_data
from utils.comments_manager import render_comment_input, render_comment_display


QUALIFICATION_TO_SCORE = {
    MarkConfig.NA.value: 2.5,
    MarkConfig.AS.value: 5.0,
    MarkConfig.AN.value: 7.5,
    MarkConfig.AE.value: 10.0
}

QUALIFICATION_ORDER = [
    MarkConfig.NA.value,
    MarkConfig.AS.value,
    MarkConfig.AN.value,
    MarkConfig.AE.value
]


def _trimester_sort_key(trimester_label):
    """Return a deterministic sort key for trimester labels such as T1, T2, T3..."""
    if not isinstance(trimester_label, str):
        return (999, str(trimester_label))

    normalized = trimester_label.strip().upper()
    t_match = re.search(r'T\s*(\d+)', normalized)
    if t_match:
        return (int(t_match.group(1)), normalized)

    digit_match = re.search(r'(\d+)', normalized)
    if digit_match:
        return (int(digit_match.group(1)), normalized)

    return (999, normalized)


def _build_comparator_dataframe(students):
    """Build a normalized dataframe used by the comparator tab."""
    normalized_students = [normalize_student_data(student) for student in students]
    rows = []

    for student in normalized_students:
        student_id = str(student.get('id', ''))
        student_name = student.get('nom_cognoms', student.get('nom', 'Sense nom'))
        trimester = student.get('trimestre', 'Sense trimestre')
        group_code = student.get('grup_codi', student.get('grup', 'Sense grup'))

        for materia in student.get('materies', []):
            qualification = materia.get('qualificacio', '')
            if qualification not in QUALIFICATION_TO_SCORE:
                continue

            rows.append({
                'AlumneId': student_id,
                'Alumne': student_name,
                'Materia': materia.get('materia', ''),
                'Qualificacio': qualification,
                'Nota': QUALIFICATION_TO_SCORE[qualification],
                'Trimestre': trimester,
                'Grup': group_code
            })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)

def display_evolution_chart(students):
    """Muestra un gráfico de evolución de las notas por trimestre"""
    # Normalize all students
    students = [normalize_student_data(s) for s in students]
    
    # Agrupar datos por trimestre y estudiante
    evolution_data = []
    for student in students:
        for materia in student['materies']:
            evolution_data.append({
                'id': student['id'],
                'nom': student['nom_cognoms'],
                'trimestre': student['trimestre'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Crear gráfico de evolución
    fig = px.line(df_evolution, 
                 x='trimestre', 
                 y='qualificacio',
                 color='materia',
                 title='Evolució de les qualificacions per trimestre',
                 labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'})
    
    st.plotly_chart(fig, config={'responsive': True}, key='evolution_chart')

def display_student_evolution(students, selected_student):
    """Muestra la evolución de las notas de un estudiante específico"""
    # Normalize all students
    students = [normalize_student_data(s) for s in students]
    
    # Filtrar datos del estudiante seleccionado
    student_data = [s for s in students if s['nom_cognoms'] == selected_student]
    
    if not student_data:
        st.warning("No se encontraron datos para el estudiante seleccionado")
        return
    
    # Preparar datos para el gráfico
    evolution_data = []
    for student in student_data:
        for materia in student['materies']:
            evolution_data.append({
                'trimestre': student['trimestre'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Crear gráfico de evolución
    fig = px.line(df_evolution, 
                 x='trimestre', 
                 y='qualificacio',
                 color='materia',
                 title=f'Evolució de les qualificacions de {selected_student}',
                 labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'})
    
    st.plotly_chart(fig, config={'responsive': True}, key='student_evolution')

def display_subject_evolution(students, selected_subject):
    """Muestra la evolución de las notas de una asignatura específica"""
    # Normalize all students
    students = [normalize_student_data(s) for s in students]
    
    # Preparar datos para el gráfico
    evolution_data = []
    for student in students:
        for materia in student['materies']:
            evolution_data.append({
                'trimestre': student['trimestre'],
                'nom': student['nom_cognoms'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Get unique subjects
    all_subjects = sorted(df_evolution['materia'].unique())
    
    # Create multi-select for subjects
    selected_subjects = st.multiselect(
        "Selecciona les materies a visualitzar",
        all_subjects,
        default=all_subjects
    )
    
    if not selected_subjects:
        st.warning("Selecciona almenys una materia per visualitzar")
        return
    
    # Filter data for selected subjects
    df_filtered = df_evolution[df_evolution['materia'].isin(selected_subjects)]
    
    # Create line plot for the selected subjects
    fig = px.line(
        df_filtered,
        x='trimestre',
        y='qualificacio',
        color='nom',
        markers=True,
        title='Evolució de les qualificacions per trimestre',
        labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'}
    )
    
    # Update layout to remove legend
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            range=[0, 10.5],
            tickvals=[2.5, 5, 7.5, 10],
            ticktext=['NA', 'AS', 'AN', 'AE']
        )
    )
    
    st.plotly_chart(fig, config={'responsive': True}, key='subject_evolution')

def display_evolution_dashboard(students, comments_manager=None):
    """Display an ordered trimester comparator (group + student evolution)."""
    st.subheader("Comparador de Trimestres")

    df = _build_comparator_dataframe(students)
    if df.empty:
        st.warning("No hi ha dades avaluables per construir el comparador")
        return

    available_groups = sorted([group for group in df['Grup'].dropna().unique() if str(group).strip()])
    if not available_groups:
        st.warning("No s'ha detectat cap grup vàlid per a la comparació")
        return

    if len(available_groups) > 1:
        selected_group = st.selectbox(
            "Selecciona el grup a comparar",
            available_groups,
            key="comparator_group_selector"
        )
    else:
        selected_group = available_groups[0]
        st.caption(f"Grup seleccionat: {selected_group}")

    df_group = df[df['Grup'] == selected_group].copy()

    ordered_trimesters = sorted(df_group['Trimestre'].unique(), key=_trimester_sort_key)
    if len(ordered_trimesters) < 2:
        st.warning("Per comparar evolució calen almenys dos trimestres del mateix grup")
        return

    trimester_position = {label: index for index, label in enumerate(ordered_trimesters)}
    df_group['TrimestrePos'] = df_group['Trimestre'].map(trimester_position)

    st.caption(f"Ordre de comparació: {' > '.join(ordered_trimesters)}")

    group_tab, student_tab = st.tabs(["Evolució del grup", "Evolució per alumne"])

    with group_tab:
        group_summary = (
            df_group
            .groupby(['TrimestrePos', 'Trimestre'], as_index=False)
            .agg(
                Mitjana=('Nota', 'mean'),
                TotalRegistres=('Nota', 'size'),
                Alumnes=('AlumneId', 'nunique'),
                Aprovats=('Nota', lambda values: (values >= 5).sum()),
                NoAssoliments=('Qualificacio', lambda values: (values == MarkConfig.NA.value).sum())
            )
            .sort_values('TrimestrePos')
        )

        group_summary['TaxaAprovat'] = (
            group_summary['Aprovats'] / group_summary['TotalRegistres'] * 100
        ).round(1)
        group_summary['TaxaNoAssoliment'] = (
            group_summary['NoAssoliments'] / group_summary['TotalRegistres'] * 100
        ).round(1)

        first_row = group_summary.iloc[0]
        last_row = group_summary.iloc[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Mitjana del grup",
                f"{last_row['Mitjana']:.2f}",
                delta=f"{last_row['Mitjana'] - first_row['Mitjana']:+.2f}"
            )
        with col2:
            st.metric(
                "Taxa d'aprovat",
                f"{last_row['TaxaAprovat']:.1f}%",
                delta=f"{last_row['TaxaAprovat'] - first_row['TaxaAprovat']:+.1f} pp"
            )
        with col3:
            st.metric(
                "Taxa de no assoliment",
                f"{last_row['TaxaNoAssoliment']:.1f}%",
                delta=f"{last_row['TaxaNoAssoliment'] - first_row['TaxaNoAssoliment']:+.1f} pp",
                delta_color="inverse"
            )

        fig_group = go.Figure()
        fig_group.add_trace(go.Scatter(
            x=group_summary['Trimestre'],
            y=group_summary['Mitjana'],
            mode='lines+markers',
            name='Mitjana del grup',
            line=dict(width=3)
        ))
        fig_group.add_trace(go.Scatter(
            x=group_summary['Trimestre'],
            y=group_summary['TaxaAprovat'],
            mode='lines+markers',
            name="Taxa d'aprovat (%)",
            yaxis='y2'
        ))
        fig_group.add_trace(go.Scatter(
            x=group_summary['Trimestre'],
            y=group_summary['TaxaNoAssoliment'],
            mode='lines+markers',
            name='Taxa no assoliment (%)',
            yaxis='y2'
        ))
        fig_group.update_layout(
            title='Evolució global del grup',
            xaxis_title='Trimestre',
            yaxis=dict(
                title='Mitjana (0-10)',
                range=[0, 10.5],
                tickvals=[2.5, 5, 7.5, 10],
                ticktext=['NA', 'AS', 'AN', 'AE']
            ),
            yaxis2=dict(
                title='Percentatge',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0)
        )
        st.plotly_chart(fig_group, config={'responsive': True}, key='comparator_group_overview')

        distribution = (
            df_group
            .groupby(['TrimestrePos', 'Trimestre', 'Qualificacio'])
            .size()
            .reset_index(name='Total')
        )

        st.subheader("Distribució de qualificacions per trimestre")
        pies_per_row = 3
        for row_start in range(0, len(ordered_trimesters), pies_per_row):
            trimester_chunk = ordered_trimesters[row_start:row_start + pies_per_row]
            cols = st.columns(len(trimester_chunk))

            for col, trimester_label in zip(cols, trimester_chunk):
                trimester_distribution = distribution[
                    distribution['Trimestre'] == trimester_label
                ].copy()

                trimester_distribution = trimester_distribution[
                    trimester_distribution['Total'] > 0
                ]

                with col:
                    if trimester_distribution.empty:
                        st.info(f"Sense dades de qualificacions per {trimester_label}")
                        continue

                    trimester_distribution = trimester_distribution.sort_values(
                        by='Qualificacio',
                        key=lambda series: series.map(
                            {label: idx for idx, label in enumerate(QUALIFICATION_ORDER)}
                        )
                    )

                    pie_colors = [
                        MarkConfig.COLOR_MAP.value.get(qual, "#808080")
                        for qual in trimester_distribution['Qualificacio']
                    ]

                    fig_pie = go.Figure(data=[go.Pie(
                        labels=trimester_distribution['Qualificacio'],
                        values=trimester_distribution['Total'],
                        hole=0.35,
                        textinfo='label+percent',
                        marker=dict(colors=pie_colors),
                        sort=False
                    )])

                    fig_pie.update_layout(
                        title=trimester_label,
                        margin=dict(t=45, b=10, l=10, r=10),
                        showlegend=False,
                        height=320
                    )

                    pie_key = f"comparator_distribution_pie_{trimester_label}".replace(" ", "_")
                    st.plotly_chart(fig_pie, config={'responsive': True}, key=pie_key)

        st.subheader("Evolució de mitjana per matèria")
        subject_summary = (
            df_group
            .groupby(['TrimestrePos', 'Trimestre', 'Materia'], as_index=False)
            .agg(Mitjana=('Nota', 'mean'))
            .sort_values(['Materia', 'TrimestrePos'])
        )

        subject_options = sorted(df_group['Materia'].unique())
        default_subjects = subject_options[: min(6, len(subject_options))]
        selected_subjects = st.multiselect(
            "Selecciona matèries",
            subject_options,
            default=default_subjects,
            key='comparator_subject_selector'
        )

        if selected_subjects:
            filtered_subject_summary = subject_summary[subject_summary['Materia'].isin(selected_subjects)]
            fig_subjects = px.line(
                filtered_subject_summary,
                x='Trimestre',
                y='Mitjana',
                color='Materia',
                markers=True,
                title='Mitjana de cada matèria al llarg dels trimestres'
            )
            fig_subjects.update_layout(
                yaxis=dict(
                    range=[0, 10.5],
                    tickvals=[2.5, 5, 7.5, 10],
                    ticktext=['NA', 'AS', 'AN', 'AE']
                )
            )
            st.plotly_chart(fig_subjects, config={'responsive': True}, key='comparator_subject_evolution')

        student_trimester = (
            df_group
            .groupby(['AlumneId', 'Alumne', 'TrimestrePos', 'Trimestre'], as_index=False)
            .agg(Mitjana=('Nota', 'mean'))
        )

        first_trimester_label = ordered_trimesters[0]
        last_trimester_label = ordered_trimesters[-1]

        first_student_trimester = student_trimester[
            student_trimester['Trimestre'] == first_trimester_label
        ][['AlumneId', 'Alumne', 'Mitjana']].rename(columns={'Mitjana': f'Mitjana {first_trimester_label}'})

        last_student_trimester = student_trimester[
            student_trimester['Trimestre'] == last_trimester_label
        ][['AlumneId', 'Alumne', 'Mitjana']].rename(columns={'Mitjana': f'Mitjana {last_trimester_label}'})

        improvement_df = first_student_trimester.merge(
            last_student_trimester,
            on=['AlumneId', 'Alumne'],
            how='inner'
        )

        if not improvement_df.empty:
            improvement_df['Evolució'] = (
                improvement_df[f'Mitjana {last_trimester_label}'] -
                improvement_df[f'Mitjana {first_trimester_label}']
            )

            top_improvement = (
                improvement_df
                .sort_values('Evolució', ascending=False)
                .head(10)
                .round(2)
            )
            top_regression = (
                improvement_df
                .sort_values('Evolució', ascending=True)
                .head(10)
                .round(2)
            )

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Alumnes que més milloren")
                st.dataframe(top_improvement, hide_index=True)
            with col2:
                st.subheader("Alumnes amb més regressió")
                st.dataframe(top_regression, hide_index=True)

    with student_tab:
        unique_students = (
            df_group[['AlumneId', 'Alumne']]
            .drop_duplicates()
            .sort_values(['Alumne', 'AlumneId'])
        )

        student_labels = [
            f"{row['Alumne']} ({row['AlumneId']})"
            for _, row in unique_students.iterrows()
        ]

        selected_student_label = st.selectbox(
            "Selecciona un alumne",
            student_labels,
            key='comparator_student_selector'
        )

        selected_student_id = selected_student_label.rsplit('(', 1)[-1].strip(')')
        df_student = df_group[df_group['AlumneId'] == selected_student_id].copy()

        student_ordered_trimesters = sorted(df_student['Trimestre'].unique(), key=_trimester_sort_key)
        student_position = {
            label: index for index, label in enumerate(student_ordered_trimesters)
        }
        df_student['TrimestrePos'] = df_student['Trimestre'].map(student_position)

        student_summary = (
            df_student
            .groupby(['TrimestrePos', 'Trimestre'], as_index=False)
            .agg(
                Mitjana=('Nota', 'mean'),
                Total=('Nota', 'size'),
                Aprovats=('Nota', lambda values: (values >= 5).sum()),
                NoAssoliments=('Qualificacio', lambda values: (values == MarkConfig.NA.value).sum())
            )
            .sort_values('TrimestrePos')
        )
        student_summary['TaxaAprovat'] = (student_summary['Aprovats'] / student_summary['Total'] * 100).round(1)

        if len(student_summary) >= 2:
            first_student_row = student_summary.iloc[0]
            last_student_row = student_summary.iloc[-1]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Mitjana alumne",
                    f"{last_student_row['Mitjana']:.2f}",
                    delta=f"{last_student_row['Mitjana'] - first_student_row['Mitjana']:+.2f}"
                )
            with col2:
                st.metric(
                    "Taxa d'aprovat",
                    f"{last_student_row['TaxaAprovat']:.1f}%",
                    delta=f"{last_student_row['TaxaAprovat'] - first_student_row['TaxaAprovat']:+.1f} pp"
                )
            with col3:
                st.metric(
                    "No assoliments",
                    f"{int(last_student_row['NoAssoliments'])}",
                    delta=f"{int(last_student_row['NoAssoliments'] - first_student_row['NoAssoliments']):+d}",
                    delta_color="inverse"
                )

        fig_student = px.line(
            df_student.sort_values(['TrimestrePos', 'Materia']),
            x='Trimestre',
            y='Nota',
            color='Materia',
            markers=True,
            title='Evolució de notes per matèria'
        )
        fig_student.update_layout(
            yaxis=dict(
                range=[0, 10.5],
                tickvals=[2.5, 5, 7.5, 10],
                ticktext=['NA', 'AS', 'AN', 'AE']
            )
        )
        st.plotly_chart(fig_student, config={'responsive': True}, key='comparator_student_evolution')

        pivot_student = (
            df_student
            .pivot_table(index='Materia', columns='Trimestre', values='Nota', aggfunc='mean')
            .reindex(columns=student_ordered_trimesters)
        )

        if len(student_ordered_trimesters) >= 2:
            start_trimester = student_ordered_trimesters[0]
            end_trimester = student_ordered_trimesters[-1]
            if start_trimester in pivot_student.columns and end_trimester in pivot_student.columns:
                pivot_student['Evolució'] = (
                    pivot_student[end_trimester] - pivot_student[start_trimester]
                )

        pivot_student = pivot_student.round(2)
        if 'Evolució' in pivot_student.columns:
            pivot_student = pivot_student.sort_values('Evolució', ascending=False)

            valid_deltas = pivot_student['Evolució'].dropna()
            if not valid_deltas.empty:
                best_subject = valid_deltas.idxmax()
                worst_subject = valid_deltas.idxmin()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Millor evolució", best_subject, f"{valid_deltas.max():+.2f}")
                with col2:
                    st.metric("Pitjor evolució", worst_subject, f"{valid_deltas.min():+.2f}")

        st.subheader("Taula de comparació per matèria")
        st.dataframe(pivot_student)

    if comments_manager and selected_group:
        comparator_session_id = f"{selected_group}_comparador"
        st.subheader("💬 Comentari del comparador")

        render_comment_display(
            comments_manager,
            "session",
            comparator_session_id,
            show_empty=False
        )

        render_comment_input(
            comments_manager,
            "session",
            comparator_session_id,
            label=f"Comentari de comparació per al grup {selected_group}",
            key_suffix="comparator",
            placeholder="Afegeix observacions sobre l'evolució entre trimestres..."
        )