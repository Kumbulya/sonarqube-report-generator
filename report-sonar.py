import requests
import argparse
import json

parser = argparse.ArgumentParser(description="Sonarqube report generator")

parser.add_argument("-u", "--url", required=True, help="Server URL")
parser.add_argument("-t", "--token", required=True, help="User token")
parser.add_argument("-p", "--projectKey", required=True, help="Sonarqube project key")
parser.add_argument("-o", "--output", help="Output file name", default="sonarqube_report.html")
parser.add_argument("-s", "--severity", help="Severity filter", default="INFO,MINOR,MAJOR,CRITICAL,BLOCKER")
parser.add_argument("--types", help="Types filter", default="CODE_SMELL,BUG,VULNERABILITY")
parser.add_argument("--style", help="Style of report", default="old")
args = parser.parse_args()  

sonarqube_server_url = str(args.url).rstrip("/")
sonarqube_acc_token = args.token
sonarqube_project_key = args.projectKey
report_filename = args.output
report_style = args.style
page = 1
page_size = 50
session = requests.Session()
session.headers.update({"Authorization":f"Bearer {sonarqube_acc_token}" })
request_string = f"{sonarqube_server_url}/api/issues/search"

report_date = ""
all_issues = []
while True:
    print(f"Запрос к странице {page}")
    sonarqube_params = {
        "componentKeys": sonarqube_project_key,
        "issuesStatuses": "OPEN",
        "severities": args.severity,
        "types": args.types,
        "ps": page_size,
        "p": page
    }
    resp = session.get(request_string, params = sonarqube_params)
    data = resp.json()
    all_issues.append(data['issues'])
    total_reports = data['total']
    if page == 1:
        print(f"Всего {total_reports} находок, будет выполнено {(total_reports + page_size - 1) // page_size} запросов")
    if total_reports < page_size*page:
        break
    page+=1

rows_html = "\n".join([f"   <tr>"
    f"<td>{row['type'] if report_style == "old" else row['impacts'][0]['softwareQuality']}</td>"
    f"<td>{row['severity'] if report_style == "old" else row['impacts'][0]['severity']}</td>"
    f"<td>{row['message']}</td>"
    f"<td>{row['component']}:{row.get('textRange', {}).get('startLine', '')}</td>"
    f"<td>{row['rule']}</td>"
    f"</tr>" 
    for issue in all_issues for row in issue])

html_report = f"""
<!DOCTYPE html> 
<html>
<head>
    <meta charset="utf-8">
    <title>Report for {sonarqube_project_key}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        
        /* Стили для панели фильтра */
        .filter-panel {{ 
            background: #f9f9f9; 
            padding: 12px; 
            border: 1px solid #ddd; 
            border-radius: 4px;
            margin-bottom: 15px;
            display: inline-block;
        }}
        .filter-panel select {{ padding: 6px 10px; font-size: 14px; min-width: 150px; }}
    </style>
</head>
<body>
    <h4>Report for {sonarqube_project_key}</h4>
    
    <!-- Панель фильтрации (список заполнится сам через JS) -->
    <div class="filter-panel">
        <label for="type-filter">Фильтр по типу уязвимости:</label>
        <select id="type-filter">
            <option value="all">Показать все</option>
        </select>
    </div>
    
    <table id="sonar-table">
        <thead>
            <tr>
                <th>Тип уязвимости</th>
                <th>Критичность</th>
                <th>Сообщение</th>
                <th>Где найдено</th>
                <th>Правило</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <script>
    document.addEventListener('DOMContentLoaded', () => {{
        const table = document.getElementById('sonar-table');
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        const filterSelect = document.getElementById('type-filter');
        
        // 1. Собираем уникальные значения из первой колонки (индекс 0)
        const uniqueTypes = new Set();
        rows.forEach(row => {{
            const cellValue = row.children[0].innerText || row.children[0].textContent;
            if (cellValue.trim()) {{
                uniqueTypes.add(cellValue.trim());
            }}
        }});
        
        // 2. Динамически добавляем найденные типы в выпадающий список <select>
        uniqueTypes.forEach(type => {{
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            filterSelect.appendChild(option);
        }});
        
        // 3. Логика фильтрации при выборе значения в выпадающем списке
        filterSelect.addEventListener('change', (e) => {{
            const selectedValue = e.target.value;
            
            rows.forEach(row => {{
                const cellValue = (row.children[0].innerText || row.children[0].textContent).trim();
                
                // Если выбрано "Показать все" или значение совпало — показываем строку, иначе скрываем
                if (selectedValue === 'all' || cellValue === selectedValue) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }});
    }});
    </script>
</body>
</html>"""

with open(report_filename, "w", encoding="utf-8") as file:
    file.write(html_report)