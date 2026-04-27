"""
Roadmap Utilities - PDF and Visual Roadmap Generation
"""
from io import BytesIO
from datetime import datetime
import re


def generate_roadmap_text(topic: str, roadmap_data: dict, progress_data: dict) -> str:
    """Generate text version of roadmap"""
    text = f"Learning Roadmap: {topic}\n"
    text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    text += f"Progress: {progress_data['percentage']:.0f}% Complete "
    text += f"({progress_data['completed_tasks']} of {progress_data['total_tasks']} tasks)\n"
    text += "=" * 60 + "\n\n"
    
    weeks = roadmap_data.get("weeks", [])
    for week in weeks:
        week_num = week.get("week", 1)
        week_title = week.get("title", f"Week {week_num}")
        tasks = week.get("tasks", [])
        
        text += f"Week {week_num}: {week_title}\n"
        text += "-" * 40 + "\n"
        
        for task in tasks:
            # Check if task is completed (you'd pass this info)
            checkbox = "✓" if False else "☐"  # Placeholder
            text += f"  {checkbox} {task}\n"
        
        text += "\n"
    
    return text


def generate_roadmap_pdf(topic: str, roadmap_data: dict, progress_data: dict, completed_tasks: set) -> BytesIO:
    """Generate PDF version of roadmap"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Title
        story.append(Paragraph(f"Learning Roadmap: {topic}", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Progress info
        progress_text = f"Progress: {progress_data['percentage']:.0f}% Complete | "
        progress_text += f"{progress_data['completed_tasks']} of {progress_data['total_tasks']} tasks completed"
        story.append(Paragraph(progress_text, styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Roadmap content
        weeks = roadmap_data.get("weeks", [])
        for week in weeks:
            week_num = week.get("week", 1)
            week_title = week.get("title", f"Week {week_num}")
            tasks = week.get("tasks", [])
            
            # Week heading
            story.append(Paragraph(f"Week {week_num}: {week_title}", heading_style))
            
            # Tasks table
            task_data = []
            for task in tasks:
                is_completed = task in completed_tasks
                checkbox = "✓" if is_completed else "☐"
                task_data.append([checkbox, task])
            
            if task_data:
                task_table = Table(task_data, colWidths=[0.5*inch, 6*inch])
                task_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(task_table)
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except ImportError:
        return None


def generate_visual_roadmap(topic: str, roadmap_data: dict) -> BytesIO:
    """Generate visual roadmap diagram"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        
        weeks = roadmap_data.get("weeks", [])
        if not weeks:
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, len(weeks) * 2 + 2))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(weeks) * 2 + 2)
        ax.axis('off')
        
        # Title
        ax.text(5, len(weeks) * 2 + 1.5, f"Learning Roadmap: {topic}", 
                ha='center', va='center', fontsize=20, fontweight='bold',
                color='#667eea')
        
        # Draw weeks
        y_pos = len(weeks) * 2
        for i, week in enumerate(weeks):
            week_num = week.get("week", i + 1)
            week_title = week.get("title", f"Week {week_num}")
            tasks = week.get("tasks", [])
            
            # Week box
            box_height = 0.3 + len(tasks) * 0.15
            box = FancyBboxPatch(
                (1, y_pos - box_height), 8, box_height,
                boxstyle="round,pad=0.1",
                edgecolor='#667eea',
                facecolor='#667eea22',
                linewidth=2
            )
            ax.add_patch(box)
            
            # Week title
            ax.text(5, y_pos - 0.15, f"Week {week_num}: {week_title}",
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='#764ba2')
            
            # Tasks
            task_y = y_pos - 0.4
            for task in tasks[:5]:  # Show max 5 tasks
                ax.text(1.5, task_y, f"• {task[:50]}{'...' if len(task) > 50 else ''}",
                        ha='left', va='center', fontsize=10, color='#333333')
                task_y -= 0.15
            
            if len(tasks) > 5:
                ax.text(1.5, task_y, f"... and {len(tasks) - 5} more tasks",
                        ha='left', va='center', fontsize=9, color='#666666', style='italic')
            
            # Arrow to next week
            if i < len(weeks) - 1:
                arrow = FancyArrowPatch(
                    (5, y_pos - box_height - 0.1),
                    (5, y_pos - box_height - 0.4),
                    arrowstyle='->,head_width=0.4,head_length=0.4',
                    color='#667eea',
                    linewidth=2
                )
                ax.add_patch(arrow)
            
            y_pos -= (box_height + 0.5)
        
        # Save to buffer
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        buffer.seek(0)
        return buffer
        
    except ImportError:
        return None


def create_download_package(topic: str, roadmap_data: dict, progress_data: dict, completed_tasks: set):
    """Create downloadable package with PDF and visual roadmap"""
    import zipfile
    
    # Generate PDF
    pdf_buffer = generate_roadmap_pdf(topic, roadmap_data, progress_data, completed_tasks)
    
    # Generate visual roadmap
    visual_buffer = generate_visual_roadmap(topic, roadmap_data)
    
    # Create ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        if pdf_buffer:
            zip_file.writestr(f"{topic.replace(' ', '_')}_roadmap.pdf", pdf_buffer.getvalue())
        
        if visual_buffer:
            zip_file.writestr(f"{topic.replace(' ', '_')}_visual.png", visual_buffer.getvalue())
        
        # Add text version
        text_content = generate_roadmap_text(topic, roadmap_data, progress_data)
        zip_file.writestr(f"{topic.replace(' ', '_')}_roadmap.txt", text_content)
    
    zip_buffer.seek(0)
    return zip_buffer
