import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.acta_loader import load_acta_csv, calculate_subject_statistics, get_student_summary


def display_acta_viewer():
    """Display the acta CSV viewer interface"""
    st.title("📋 Visualitzador d'Actes d'Avaluació")
    
    # Welcome message
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
        <h3 style='margin: 0; color: white; border: none;'>👋 Carrega actes d'avaluació</h3>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>Carrega fitxers CSV d'actes per analitzar les qualificacions dels alumnes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Carrega un fitxer CSV d'acta",
        type=['csv'],
        help="Selecciona un fitxer CSV exportat d'Esfera"
    )
    
    if not uploaded_file:
        st.info("👆 Carrega un fitxer CSV per començar")
        return
    
    # Load and parse the CSV
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        data = load_acta_csv(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Display metadata
        with st.expander("ℹ️ Informació de l'acta", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 0.9em; color: #666;'>Grup</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: bold;'>{data['metadata']['grup_codi']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 0.9em; color: #666;'>Avaluació</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: bold;'>#{data['metadata']['numero_avaluacio']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 0.9em; color: #666;'>Alumnes</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: bold;'>{len(data['students'])}</p>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 0.9em; color: #666;'>Matèries</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: bold;'>{len(data['subjects'])}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📊 Vista Global", "📚 Per Matèria", "👤 Per Alumne"])
        
        with tab1:
            display_global_view(data)
        
        with tab2:
            display_subject_view(data)
        
        with tab3:
            display_student_view(data)
        
    except Exception as e:
        st.error(f"❌ Error carregant el fitxer: {str(e)}")
        st.exception(e)


def display_global_view(data):
    """Display global statistics view"""
    st.markdown("### 📊 Estadístiques Globals")
    
    students = data['students']
    
    # Calculate global statistics
    total_passed = 0
    total_failed = 0
    total_pending = 0
    total_convalidated = 0
    all_grades = []
    
    for student in students:
        summary = get_student_summary(student)
        total_passed += summary['passed_count']
        total_failed += summary['failed_count']
        total_pending += summary['pending_count']
        all_grades.extend([m['nota'] for m in student['materies'] if m['qualificacio_status'] == 'Assolit'])
    
    # Count convalidated across all students and subjects
    for student in students:
        for materia in student['materies']:
            if materia['qualificacio_status'] == 'Convalidat':
                total_convalidated += 1
    
    # Display summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("✅ Assolides", total_passed)
    with col2:
        st.metric("❌ No Assolides", total_failed)
    with col3:
        st.metric("⏳ Pendents", total_pending)
    with col4:
        st.metric("📝 Convalidades", total_convalidated)
    with col5:
        avg = sum(all_grades) / len(all_grades) if all_grades else 0
        st.metric("📈 Mitjana", f"{avg:.2f}")
    
    st.markdown("---")
    
    # Distribution chart
    st.markdown("#### 📊 Distribució de Qualificacions")
    
    labels = ['Assolides', 'No Assolides', 'Pendents', 'Convalidades']
    values = [total_passed, total_failed, total_pending, total_convalidated]
    colors = ['#2ca02c', '#d62728', '#ff7f0e', '#1f77b4']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        textfont=dict(size=14, color='white')
    )])
    
    fig.update_layout(
        template='plotly_white',
        showlegend=True,
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, config={'responsive': True})
    
    # Grades distribution histogram
    if all_grades:
        st.markdown("---")
        st.markdown("#### 📈 Distribució de Notes")
        
        fig = go.Figure(data=[go.Histogram(
            x=all_grades,
            nbinsx=10,
            marker_color='#1f77b4',
            opacity=0.75
        )])
        
        fig.update_layout(
            template='plotly_white',
            xaxis_title="Nota",
            yaxis_title="Freqüència",
            height=400,
            bargap=0.1
        )
        
        st.plotly_chart(fig, config={'responsive': True})
    
    # Student rankings
    st.markdown("---")
    st.markdown("#### 🏆 Rànquing d'Alumnes")
    
    student_rankings = []
    for student in students:
        summary = get_student_summary(student)
        student_rankings.append({
            'Alumne': student['nom_cognoms'],
            'Assolides': summary['passed_count'],
            'No Assolides': summary['failed_count'],
            'Mitjana': f"{summary['avg_grade']:.2f}" if summary['avg_grade'] > 0 else 'N/A'
        })
    
    df_rankings = pd.DataFrame(student_rankings)
    df_rankings = df_rankings.sort_values('Mitjana', ascending=False, key=lambda x: pd.to_numeric(x.replace('N/A', '0')))
    
    st.dataframe(df_rankings, hide_index=True, height=400)


def display_subject_view(data):
    """Display subject-specific view"""
    st.markdown("### 📚 Anàlisi per Matèria")
    
    subjects = data['subjects']
    students = data['students']
    
    if not subjects:
        st.info("No s'han trobat matèries")
        return
    
    # Subject selector
    selected_subject = st.selectbox(
        "📖 Selecciona una matèria:",
        subjects,
        key="acta_subject_selector"
    )
    
    # Calculate statistics for selected subject
    stats = calculate_subject_statistics(students, selected_subject)
    
    st.markdown("---")
    st.markdown(f"#### 📊 Estadístiques de **{selected_subject}**")
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Total", stats['count_total'])
    with col2:
        st.metric("✅ Assolides", stats['count_assolit'])
    with col3:
        st.metric("❌ No Assolides", stats['count_no_assolit'])
    with col4:
        st.metric("⏳ Pendents", stats['count_pendent'])
    with col5:
        st.metric("📈 Mitjana", f"{stats['avg_grade']:.2f}" if stats['avg_grade'] > 0 else 'N/A')
    
    # Pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Distribució")
        
        labels = []
        values = []
        colors = []
        
        if stats['count_assolit'] > 0:
            labels.append('Assolides')
            values.append(stats['count_assolit'])
            colors.append('#2ca02c')
        if stats['count_no_assolit'] > 0:
            labels.append('No Assolides')
            values.append(stats['count_no_assolit'])
            colors.append('#d62728')
        if stats['count_pendent'] > 0:
            labels.append('Pendents')
            values.append(stats['count_pendent'])
            colors.append('#ff7f0e')
        if stats['count_convalidat'] > 0:
            labels.append('Convalidades')
            values.append(stats['count_convalidat'])
            colors.append('#1f77b4')
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=.4,
            textinfo='label+percent+value',
            textfont=dict(size=13, color='white')
        )])
        
        fig.update_layout(
            template='plotly_white',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, config={'responsive': True})
    
    with col2:
        st.markdown("#### 👥 Llista d'Alumnes")
        
        # Create detailed table
        subject_details = []
        for student in students:
            for materia in student['materies']:
                if materia['materia'] == selected_subject:
                    subject_details.append({
                        'Alumne': student['nom_cognoms'],
                        'Qualificació': materia['qualificacio_status'],
                        'Nota': f"{materia['nota']:.1f}" if materia['nota'] > 0 else '-',
                        'Comentari': materia['comentari'][:50] + '...' if len(materia['comentari']) > 50 else materia['comentari']
                    })
        
        df_details = pd.DataFrame(subject_details)
        df_details = df_details.sort_values('Alumne')
        
        st.dataframe(df_details, hide_index=True, height=350)


def display_student_view(data):
    """Display student-specific view"""
    st.markdown("### 👤 Anàlisi per Alumne")
    
    students = data['students']
    
    if not students:
        st.info("No s'han trobat alumnes")
        return
    
    # Student selector
    student_names = [f"{s['nom_cognoms']} ({s['id']})" for s in students]
    selected_student_name = st.selectbox(
        "👤 Selecciona un alumne:",
        student_names,
        key="acta_student_selector"
    )
    
    # Find selected student
    selected_id = selected_student_name.split('(')[-1].strip(')')
    selected_student = next(s for s in students if s['id'] == selected_id)
    
    # Calculate summary
    summary = get_student_summary(selected_student)
    
    st.markdown("---")
    
    # Student header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;'>
        <h2 style='margin: 0 0 15px 0; color: white; border: none;'>🎓 {selected_student['nom_cognoms']}</h2>
        <p style='margin: 0; opacity: 0.9; font-size: 1.1em;'>ID: {selected_student['id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📚 Total Matèries", summary['total_subjects'])
    with col2:
        st.metric("✅ Assolides", summary['passed_count'])
    with col3:
        st.metric("❌ No Assolides", summary['failed_count'])
    with col4:
        pass_rate = (summary['passed_count'] / summary['total_subjects'] * 100) if summary['total_subjects'] > 0 else 0
        st.metric("📊 Taxa èxit", f"{pass_rate:.1f}%")
    with col5:
        st.metric("📈 Mitjana", f"{summary['avg_grade']:.2f}" if summary['avg_grade'] > 0 else 'N/A')
    
    # Distribution and subjects table
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📊 Distribució")
        
        labels = []
        values = []
        colors = []
        
        if summary['passed_count'] > 0:
            labels.append('Assolides')
            values.append(summary['passed_count'])
            colors.append('#2ca02c')
        if summary['failed_count'] > 0:
            labels.append('No Assolides')
            values.append(summary['failed_count'])
            colors.append('#d62728')
        if summary['pending_count'] > 0:
            labels.append('Pendents')
            values.append(summary['pending_count'])
            colors.append('#ff7f0e')
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=.4,
            textinfo='label+percent+value',
            textfont=dict(size=12, color='white')
        )])
        
        fig.update_layout(
            template='plotly_white',
            showlegend=False,
            height=350,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        
        st.plotly_chart(fig, config={'responsive': True})
    
    with col2:
        st.markdown("#### 📚 Matèries")
        
        # Create subjects table
        subjects_data = []
        for materia in selected_student['materies']:
            subjects_data.append({
                'Matèria': materia['materia'],
                'Estat': materia['qualificacio_status'],
                'Nota': f"{materia['nota']:.1f}" if materia['nota'] > 0 else '-',
                'Comentari': materia['comentari'][:40] + '...' if len(materia['comentari']) > 40 else materia['comentari']
            })
        
        df_subjects = pd.DataFrame(subjects_data)
        
        # Add color coding
        def highlight_status(row):
            colors_map = {
                'Assolit': 'background-color: #ccffcc',
                'No assolit': 'background-color: #ffcccc',
                'Pendent': 'background-color: #ffe6cc',
                'Convalidat': 'background-color: #cce5ff'
            }
            return [colors_map.get(row['Estat'], '')] * len(row)
        
        styled_df = df_subjects.style.apply(highlight_status, axis=1)
        
        st.dataframe(styled_df, hide_index=True, height=330)
    
    # Comments section
    if selected_student.get('comentari_general', '').strip():
        st.markdown("---")
        st.markdown("#### 💬 Comentari General")
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; 
                    border-left: 5px solid #1f77b4;'>
            <p style='margin: 0; line-height: 1.6;'>{selected_student['comentari_general']}</p>
        </div>
        """, unsafe_allow_html=True)
