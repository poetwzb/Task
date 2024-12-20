import requests
from bs4 import BeautifulSoup
import pandas as pd

# Build request header. Forge headers to bypass this anti-climbing mechanism
headers = {
    # Specifies the type of response content acceptable to the client
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # Used to track user sessions
    'Cookie': 'JSESSIONID=5A45096BF97599283003FB8692622942; atlassian.xsrf.token=A5KQ-2QAV-T4JA-FDED_06bd14a3e621c8b26009b2e2c1b72a931ae10268_lout; _ga=GA1.2.1516036890.1711357731; _ga_K3S5WD0QC1=GS1.2.1711357735.1.0.1711357735.60.0.0',
    # Identifies the page from which the request is directed
    'Referer': 'https://issues.apache.org/jira/browse/CAMEL-10597',
    # Specifies the destination of the resource request
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    # Set the User-Agent of the Chrome browser
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'X-AUSERNAME': '',
    'X-PJAX': 'true',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

url = "https://issues.apache.org/jira/browse/CAMEL-10597"
# Send HTTP requests to get web content
response = requests.get(url)
if response.status_code == 200:
    # Parse a web page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    # 1. Details
    mod_content = soup.select_one('.mod-content')
    issue_data = {}
    if mod_content:
        items = mod_content.find_all('li', class_='item')
        for item in items:
            field_name_element = item.find('strong', class_='name')
            if field_name_element:
                field_name = field_name_element.text.strip().replace(":", "")
                if field_name == "Patch Info":
                    patch_info_element = item.find('div', class_='shorten')
                    if patch_info_element:
                        patch_info_value = patch_info_element.find('span').get_text(strip=True)
                    else:
                        patch_info_value = None
                    issue_data[f"Details.{field_name}"] = patch_info_value
                elif field_name == "Estimated Complexity":
                    complexity_element = item.find('div', class_='value')
                    if complexity_element:
                        complexity_value = complexity_element.get_text(strip=True)
                    else:
                        complexity_value = None
                    issue_data[f"Details.{field_name}"] = complexity_value
                    continue
                else:
                    field_value_element = item.find('span', class_='value')
                    if field_value_element:
                        field_value = field_value_element.text.strip()
                    else:
                        field_value = None
                    issue_data[f"Details.{field_name}"] = field_value

    # 2.people
    people_module = soup.find(id="peoplemodule")
    if people_module:
        people_data = {}
        assignee_element = people_module.find('span', id="assignee-val")
        if assignee_element:
            assignee_name = assignee_element.get_text(strip=True)
            people_data["People.Assignee"] = assignee_name
        reporter_element = people_module.find('span', id="reporter-val")
        if reporter_element:
            reporter_name = reporter_element.get_text(strip=True)
            people_data["People.Reporter"] = reporter_name
        votes_element = people_module.find('aui-badge', id="vote-data")
        if votes_element:
            votes_count = votes_element.text.strip()
            people_data["People.Votes"] = votes_count
        watchers_element = people_module.find('aui-badge', id="watcher-data")
        if watchers_element:
            watchers_count = watchers_element.text.strip()
            people_data["People.Watchers"] = watchers_count
        issue_data.update(people_data)
    for key, value in issue_data.items():
        print(f"{key}: {value}")

    # 3.Dates
    dates_module = soup.find(id="datesmodule")
    if dates_module:
        date_info = {}
        date_elements = dates_module.find_all('dl', class_='dates')
        for date_element in date_elements:
            date_type = date_element.find('dt').text.strip()
            date_type_cleaned = date_type.rstrip(':')
            date_value_element = date_element.find('dd', class_='date')
            if date_value_element:
                date_value = date_value_element.find('time').text.strip()
                date_info[f"Dates.{date_type_cleaned}"] = date_value
        issue_data.update(date_info)

    # 4.Describle
    description_module = soup.find(id="descriptionmodule")
    description_content = []
    if description_module:
        description_val = description_module.find('div', id='description-val')
        if description_val:
            paragraphs = description_val.find_all('p')
            for paragraph in paragraphs:
                description_content.append(paragraph.text.strip())
            code_blocks = description_val.find_all('pre')
            for code_block in code_blocks:
                code_text = code_block.get_text(strip=True)
                description_content.append(f"Code block:\n{code_text}\n")
    issue_data["Description"] = " ".join(description_content) if description_content else None

    # 4. Issue Links
    issue_links = []
    linking_module = soup.find(id="linkingmodule")
    if linking_module:
        links_container = linking_module.find('div', class_='links-container')
        if links_container:
            links = links_container.find_all('dd', class_='remote-link')
            for link in links:
                link_content = link.find('a', class_='link-title')
                if link_content:
                    link_url = link_content.get('href')
                    link_title = link_content.text.strip()
                    issue_links.append(f"links to {link_title} {link_url}")
    if issue_links:
        issue_data["Issue Links"] = " | ".join(issue_links)

    # 5. Comments
    url = 'https://issues.apache.org/jira/browse/CAMEL-10597?page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel&_=1734585525752'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all('div', class_='action-body')
    comment_data = []
    activity_comments = {}
    for comment in comments:
        author_tag = comment.find_previous('a', class_='user-hover')
        author_name = author_tag.get_text(strip=True) if author_tag else "Unknown"
        time_tag = comment.find_previous('time', class_='livestamp')
        comment_time = time_tag['datetime'] if time_tag else "Unknown Time"
        comment_body = comment.get_text(strip=True) if comment else "No comment content"
        pr_link_tag = comment.find('a', class_='external-link')
        pr_link = pr_link_tag['href'] if pr_link_tag else None
        pr_info = None
        if pr_link:
            if "opened" in comment_body:
                pr_info = f"GitHub user {author_name} opened a pull request:\n\n{pr_link}\n\n{comment_body}"
            elif "closed" in comment_body:
                pr_info = f"GitHub user {author_name} closed the pull request at:\n\n{pr_link}\n\n{comment_body}"
            elif "Thanks for the PR" in comment_body:
                pr_info = f"Thanks for the PR: {pr_link}"
            elif "included" in comment_body:
                pr_info = f"PR included {pr_link}"
        else:
            pr_info = comment_body
        comment_key = f"Activity.Comment.{author_name} added a comment - {comment_time}"
        activity_comments[comment_key] = pr_info
        comment_data.append({
            'author': author_name,
            'time': comment_time,
            'comment': comment_body,
            'pr_link': pr_link,
        })
    issue_data.update(activity_comments)

    # for data in comment_data:
    #     print(f"Author: {data['author']}")
    #     print(f"Time: {data['time']}")
    #     print(f"Comment: {data['comment']}")
    #     if data['pr_link']:
    #         print(f"PR Link: {data['pr_link']}")
    #     print('-' * 80)

    # 6.work log
    url = 'https://issues.apache.org/jira/browse/CAMEL-10597?page=com.atlassian.jira.plugin.system.issuetabpanels:worklog-tabpanel&_=1734585525742'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        worklog_tab = soup.find('li', {'id': 'worklog-tabpanel'})
        if worklog_tab:
            worklog_link = worklog_tab.find('a')
            if worklog_link and worklog_link.text.strip() == 'Work Log':
                print("Work Log The TAB has no content and appears empty")
                work_log_data = "No work has yet been logged on this issue."
            else:
                work_log_data = worklog_tab.text.strip()
                print("Work Log TAB contents：")
                print(work_log_data)
        else:
            print("The Work Log TAB was not found。")
            work_log_data = "No work has yet been logged on this issue."
        issue_data["WorkLog"] = work_log_data
    else:
        print(f"Request failed, status code: {response.status_code}")
        work_log_data = "Failed to retrieve work log data"
        issue_data["Activity.worklog"] = work_log_data

    # 7.history
    url = 'https://issues.apache.org/jira/browse/CAMEL-10597?page=com.atlassian.jira.plugin.system.issuetabpanels:changehistory-tabpanel&_=1734585525745'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        change_blocks = soup.find_all('div', class_='issue-data-block')
        change_history_data = ""
        for change_block in change_blocks:
            author = change_block.find('a', class_='user-hover')
            date = change_block.find('time', class_='livestamp')
            changes = change_block.find_all('tr')
            author_name = author.get_text(strip=True) if author else "Unknown"
            change_date = date.get_text(strip=True) if date else "Unknown Date"
            change_history_data += f"Change Author: {author_name}\nChange Date: {change_date}\n"
            for change in changes:
                field = change.find('td', class_='activity-name')
                old_value = change.find('td', class_='activity-old-val')
                new_value = change.find('td', class_='activity-new-val')
                if field and old_value and new_value:
                    change_history_data += f"Field: {field.get_text(strip=True)}\n"
                    change_history_data += f"Old Value: {old_value.get_text(strip=True)}\n"
                    change_history_data += f"New Value: {new_value.get_text(strip=True)}\n"
            change_history_data += "-" * 50 + "\n"
    else:
        change_history_data = "Failed to retrieve change history data"
    history_data = f"Work Log Data:\n{work_log_data}\n\nChange History Data:\n{change_history_data}"
    issue_data["Activity.history"] = history_data

    # 8.activity
    url = 'https://issues.apache.org/jira/browse/CAMEL-10597?page=com.atlassian.streams.streams-jira-plugin:activity-stream-issue-tab&_=1734585525740'
    response = requests.get(url, headers=headers)
    activity_url = ""
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        activity_content = soup.find('iframe', {'id': 'gadget-0'})
        if activity_content:
            activity_url = ""
        else:
            print("The Activity TAB content was not found")
            activity_url = ""
    else:
        print(f"Request failed, status code: {response.status_code}")
    issue_data["Activity.Activity"] = activity_url

    # 9.transition
    url = 'https://issues.apache.org/jira/browse/CAMEL-10597?page=com.googlecode.jira-suite-utilities:transitions-summary-tabpanel&_=1734585525746'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        action_details = soup.find_all('div', class_='action-details')
        transition_data = ""
        for detail in action_details:
            user_info = detail.find('a', class_='user-hover')
            user = user_info.get_text(strip=True) if user_info else 'Unknown User'
            time_info = detail.find('time', class_='livestamp')
            transition_time = time_info.get_text(strip=True) if time_info else 'Unknown Time'
            status_td = soup.find_all('td', width='47%')
            if len(status_td) >= 2:
                from_status = status_td[0].find('span', class_='jira-issue-status-lozenge').get_text(strip=True)
                to_status = status_td[1].find('span', class_='jira-issue-status-lozenge').get_text(strip=True)
            else:
                print("No valid status information found")
            time_in_source_status = detail.find_next('td', width="20%")
            execution_times = time_in_source_status.find_next('td', width="20%") if time_in_source_status else None
            if time_in_source_status and execution_times:
                time_in_status = time_in_source_status.get_text(strip=True)  # "49m 49s"
                execution_count = execution_times.get_text(strip=True)  # "1"
            else:
                time_in_status = 'Unknown Time'
                execution_count = '0'
            transition_data += f"{user} made transition - {transition_time}\n"
            transition_data += f"Transition: {from_status} to {to_status}\n"
            transition_data += f"Time In Source Status: {time_in_status}\n"
            transition_data += f"Execution Times: {execution_count}\n"
            transition_data += "-" * 80 + "\n"
    else:
        transition_data = "Failed to retrieve transition data"
    issue_data["Activity.Transitions"] = transition_data

    # 10. 表格创建
    excel_filename = "jira_issue_data.csv"
    issue_df = pd.DataFrame([issue_data])
    issue_df.to_csv("jira_issue_data.csv", index=False)
    print(f"Excel document {excel_filename} successfully generated！")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
















