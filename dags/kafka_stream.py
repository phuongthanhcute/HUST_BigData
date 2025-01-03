from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import time
from datetime import datetime, timedelta
import random

# -------------------CRAWL DATA-----------------------------------------------------------
import requests
from bs4 import BeautifulSoup

TIME_SLEEP = 5
TIME_STREAM = 55

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

    # ,
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    # "Accept-Encoding": "gzip, deflate, br",
    # "Accept-Language": "en-US,en;q=0.9",
    # "Connection": "keep-alive"
def get_list_link_page(start, end):
    links = []
    for i in range(start, end + 1):
        links.append(
            "https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026?salary=0&exp=0&company_field=0&sort=up_top&page=" + str(
                i))
    return links

def get_links_company(list_link_page):
    def get_titles(list_link_page):
        titles = []
        for link in list_link_page:
            print("link page: " + link)
            while True:
                response = requests.get(link, headers = headers)
                print("response.status: " + str(response.status_code))
                if response.status_code not in range(200, 300) :
                    print(f'sleep {TIME_SLEEP} s')
                    time.sleep(TIME_SLEEP)
                    continue
                
                soup = BeautifulSoup(response.content, "html.parser")
                title = soup.findAll('h3', class_='title')
                for tit in title:
                    titles.append(tit)
                break
        return titles

    links_company = []
    for link_company in get_titles(list_link_page):
        link_obj = link_company.find('a', href=True)
        if link_obj != None:
            link = link_obj['href']
            links_company.append(link)
    return links_company


def get_data(link):
    # data = {
    #     "id": time.time(),
    #     "name": "Công ty Cổ phần S.I.S Việt Nam",
    #     "mo_ta_cong_viec": "Lập trình viên :· Trực tiếp tham gia vào các dự án phát triển sản phẩm CRM, ERP… của Công ty trên nền tảng C#, MVC 5, ASP.NET, Winform· Tham gia làm rõ nghiệp vụ, thiết kế giải pháp, phát triển nâng cấp hệ thống theo yêu cầu· Tham gia review thiết kế, review code, tối ưu hệ thống đáp ứng lưu lượng truy cập cao· Nghiên cứu áp dụng công nghệ mới nâng cao chất lượng, tối ưu nguồn lực phát triểnKĩ thuật bảo hành phần mềm· Hỗ trợ, xử lý kĩ thuật cho khách hàng trong quá trình sử dụng phần mềm do SISVN cung cấp· Tư vấn các giải pháp để khách hàng sử dụng phần mềm một cách tối ưu và hiệu quả nhất",
    #     "yeu_cau_cong_viec": "· Tốt nghiệp chuyên ngành CNTT· Ưu tiên ứng viên có hiểu biết về kế toán và quản trị doanh nghiệp",
    #     "quyen_loi": "· Lương cứng (12 - 18 triệu) + % thưởng theo dự án· Thưởng quý cao theo hiệu quả công việc· Được làm việc trong môi trường nhiều thử thách, chuyên nghiệp nhưng hòa đồng, có cơ hội được đào tạo nâng cao nghiệp vụ chuyên môn thường xuyên, đặc biệt là chuyên ngành công nghệ và kế toán· Được tham gia các dự án lớn, quy mô, ở nhiều tỉnh/ thành phố tại Việt Nam· Chế độ BHXH theo QĐ của nhà nước · Nghỉ phép năm 12 ngày/năm và lễ tết theo quy định của Công ty.· Các chế độ du lịch, team building hàng năm, văn hóa thể thao theo quy định công ty",
    #     "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 08/08/2022"
    #     "Địa điểm làm việc: "",
    #     "Thời gian làm việc: ""
    # }
    # return data
    print("link_company: " + str(link))
    company_data = {}

    while True:
        response_news = requests.get(link, headers = headers)
        print("response.status: " + str(response_news.status_code))
        if response_news.status_code not in range(200, 300):
            print(f'sleep {TIME_SLEEP} s')
            time.sleep(TIME_SLEEP)
            continue
        
        soup = BeautifulSoup(response_news.content, "html.parser")

        # lấy tên công ty
        name_label = soup.find('h2', class_="company-name-label")
        if name_label is None:
            break
        
        name = name_label.find('a').get_text(strip=True)
        # lấy các thông tin về job
        contents = soup.find("div", class_="job-detail__information-detail")

        company_data['id'] = time.time()
        company_data['name'] = name
        add_contents(contents, company_data)
        break
    return company_data

def add_contents(contents, data):
    node_tag = contents.find('div', class_="job-tags")
    # if node_tag:
    #     text = node_tag.find('a').get_text(strip = True)
    #     data['tags'] = text

    node_job_description = contents.find('div', class_='job-description')
    for header in node_job_description.find_all('h3'):
        item_name = header.get_text(strip=True)

        # duyệt qua các node cùng cấp tiếp theo lấy tất cả các text
        nextNode = header
        content = ""
        while True:
            nextNode = nextNode.nextSibling
            if nextNode is None:
                break
            
            content += " ".join(nextNode.stripped_strings)
        data[item_name] = content

def get_data_f():
    data = random.choice(raw_data)
    data['id'] = time.time()
    return data
# ------------------------------------------------------------------------------

default_args = {
    'owner': 'tandat17z',
    'start_date': datetime(2024, 12, 22, 10, 00),
    'retries': 5,
    'retry_delay': timedelta(minutes = 2)
}

def stream_data():
    import json
    from kafka import KafkaProducer

    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    
    # start = 1
    # end = 5
    # links_page = get_list_link_page(start, end)
    # links_company = get_links_company(links_page)


    # for link in links_company:
    #     try:
    #         res = get_data(link)
    #         if res is not None:
    #             producer.send('recruitment_information', json.dumps(res).encode('utf-8'))
    #             time.sleep(3)
    #     except Exception as e:
    #         print(f'An error occured: {e}')
    #         continue

    curr_time = time.time()
    while True:
        if time.time() > curr_time + TIME_STREAM: #1 minute
            break

        try:
            res = get_data_f()

            producer.send('recruitment_information', json.dumps(res).encode('utf-8'))
            time.sleep(TIME_SLEEP)
        except Exception as e:
            print(f'An error occured: {e}')


with DAG('stream_recruitment_information',
         default_args=default_args,
         description = "This is kafka stream task.",
         schedule_interval='* * * * *',
         catchup=False) as dag:

    streaming_task = PythonOperator(
        task_id='stream_job_data',
        python_callable=stream_data
    )

    streaming_task



















































































































































































































































































































































































































































































































































































































































































































































































































raw_data = [
    {
  "name": "VNDIRECT",
  "mo_ta_cong_viec": "TEAMOur Digital Product team advocates for our users and business, setting the vision for our growing family of innovative products. We use data, research, strategy, and empathy to guide multidisciplinary teams toward a common goal, balancing diverse perspectives and empowering our teams to do great work. As we scale, there’s plenty of space for you to grow alongside us and simplify life for millions of people; in a team that always focuses on we, not I, and creates delightful products that are worthy of trust.ROLE DESCRIPTIONWe are looking for a Senior Design Manager to join the UX & Design team at VNDIRECT - a group that enables all of VNDIRECT to build cohesive, user-centered products, by maintaining a unified design system and cultivating a thriving design community. Your key focus area will be leading our cross-team initiative to build and refresh VNDIRECT‘s design system, working with teams of designers, engineers, and product managers to create a system and home for the tools, guidelines, components, and patterns that we use to build VNDIRECT digital products for our users.You‘ll establish efficient and effective working practices between the teams that contribute to our design systems, and amplify the effectiveness of this complex, cross-disciplinary program. Your secondary focus will be streamlining our design tools and helping the design operations team establish best practices in how we use these tools or expand the set to keep us innovating.RESPONSIBILITIES- Build and evolve our Design System deliverables to be scalable, innovative, and user-friendly for customers and applicable for the stakeholders.- Collaborate closely with a multidisciplinary team to arrive at global reusable design patterns that are innovative and intuitive for customers- Work creatively around difficult business and technical constraints to maintain a high customer experience bar- Write, update, and maintain the library of documentation associated with the design system- Get buy-in from key decision-makers to push forward design system initiatives that align with product teams or technology functions and drive the executions- Drive the overall system roadmap: helping teams define scope, deliverables, and schedules, and coordinating release planning across multiple teams for multiple stakeholders- Create and socialize processes for how designers and engineers will adapt and contribute to the system- Organise roadshows and trainings on the design system for our product teams- Define and track KPIs to monitor the success of the design system product and find creative ways to help the system teams connect with their objectives.- Create and maintain comprehensive visual audits of our products and flows QA work to ensure designs and creative assets are rendered appropriately in the digital products- Keep up to date with the latest design trends and tools and make proposals about why VNDIRECT should invest in new tools, and how we make them work for our teams‘ ways of working.- Define and run the overall Design Operations practice- Define and manage strategic initiatives that improve design team efficiency and impact- Collaborate cross-functionally with designers, developers, researchers, writers, and product managers to ensure a smooth design process",
  "yeu_cau_cong_viec": "REQUIREMENTS- At least 7+ years of experience in product design-related field- Experience shipping innovative, successful mass consumer products in a highly-matrixed and ambiguous environment- Exposure to a revamp project, designing a User Interface in a system- Have built or managed a design system team- Experience with design systems and/or brand style guides- Have experience setting up design ops for diverse product teams- You are enthusiastic about details - a pixel perfectionist!- Proficiency in visual design - iconography, UI, logos, layout- Demonstrated ability to document and share processes- Proven cross-functional skills and experience in stakeholder management- Proficiency in design tools: Figma, Sketch, Photoshop, Illustrator- Familiarity with prototyping tools (ie Principle, Origami, Invision, Framer)- Comfortable in an ambiguous work environment.",
  "quyen_loi": "ALL OF OUR JOBS REQUIRE-GreatcommunicationWe’re a diversified team, so clear communication is a must.-Self-driven work ethic yet strongcollaboration. You need to be a self-starter who loves taking the initiative and seeing things through to completion.-CriticalWe are in a complex business; we need everyone to be reflective, independent, and competent.-Curiosity and the desire to learn and to becreative. Our business is changing and growing fast; who knows what will be the skills of tomorrow? Flexibility is key.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 11/08/2022"
},
{
  "name": "FPT Software",
  "mo_ta_cong_viec": "Kỹ thuật liên quan đến hệ thống SAP ERPPhân tích logic, hệ thống hóa từ yêu cầu thành phần mềm.Viết tài liệu Unit Test case.Thuyết trình, trình bày các nội dung trong công việc thực tiễn.Được training về ngôn ngữ lập trình ABAP trên hệ thống SAP",
  "yeu_cau_cong_viec": "Sinh viên đang theo học cao đẳng, đại học với chuyên ngành Kế toán, Kiểm toán, Ngân hàng, Tài chính, Hệ thống thông tin, Công nghệ thông tin hoặc các chuyên ngànhGiao tiếp và đọc hiểu tiếng Anh, ưu tiên các bạn có Toiec 600 trở lên hoặc chứng chỉ tương đươngLợi thế với các kiến thức về lập trình C#, Web, SQL Server, Azure.Cẩn thận, tỉ mỉ trong công việc.Chịu áp lực công việc và sẵn sàng sắp xếp thời gian theo yêu cầu dự án.Sử dụng thành thạo MS Excel, MS Word, MS Powerpoint",
  "quyen_loi": "Tham gia khóa training trước khi làm việc tại đơn vị với mức hỗ trợ đào tạo lên đến 20.000.000/khóa.Sau khi kết thúc đào tạo tại FSOFT Academy: Tham gia làm việc tại các dự án với mức thu nhập hấp dẫn tương xứng với kỹ năng và kinh nghiệm của bạn, trung bình từ 8.000.000 VNĐ – 15.000.000 VNĐ/tháng. Thu nhập trung bình 1 năm từ 13-18 tháng lương, tùy theo kết quả đào tạo và làm việc.Hưởng các chính sách như: Hỗ trợ thi các chứng chỉ chuyên nghiệp quốc tế, hỗ trợ mua nhà, bảo hiểm FPT care…Cơ hội phát triển bản thân và làm việc cùng các chuyên gia của FPT Software và khách hàng lớn đến từ Mỹ, Pháp, Singapore, Nhật Bản…Trải nghiệm văn hóa đặc trưng, môi trường làm việc hiện đại bậc nhất Việt Nam tại các Campus của FPT Software",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "FPT Software",
  "mo_ta_cong_viec": "FPT Software Hà Nộicần tuyển 15 Lập trình viên Embedded Automation Testing tham gia Chương trình đào tạo tân binh và làm việc trực tiếp tại các dự án hàng đầu trong lĩnh vực Automotive – phát triển công nghệ cho xe hơi thông minh hạng sang: Tham gia kiểm thử và phát triển các phần mềm Nhúng cho hệ thống điều khiển, kiểm soát an toàn cho xe hơi, hệ thống thông tin giải trí trong ô tô (media, video, audio), hệ thống định vị và dẫn đường (navigation), phát triển Middleware drivers cho các hệ thống GPS, Radio (AM/FM), Digital Radio (DAB/MDB), Bluetooth, Wifi…) và tham gia kiểm thử và phát triển platform cho các thiết bị IoT.Chương trình đào tạo tân binh Fresher Embedded Automation Testinglà chương trình được xây dựng nhằm giúp các tân binh của FPT Software có cơ hội tìm hiểu và hệ thống lại các kiến thức liên quan đến kiểm thử tự động và học hỏi quy trình phát triển phần mềm trước khi tham gia vào các dự án thực tế trong lĩnh vực Automotive. Nội dung phần training bao gồm các phần:Software Testing FoundationTest Concept and Principle ProcessTest Level, Test Type and TechniqueSW Requirement for Tester (SWRT)Test Design & Test CaseTest Execution & Defect managementAutomation testing for IoT, Embedded systemPrograming language: Python and testing framework: SWTBot, Pytest…CI/CD Framework and Tools (Jenkins, Git, Jira)Automation testing tools for IoT, Embedded systemPhát triển phần mềm theo quy trình chuyên nghiệpHiểu các bước thực hiện dự án, bao gồm thiết kế ứng dụng, làm GUI, thiết kế code, thực hiện Unit test, kiểm tra chất lượng dự án.Luyện tập kỹ năng code trong dự án.Rèn luyện các kỹ năng mềm: Viết email, kỹ năng phỏng vấn, thuyết trình, kỹ năng phân tích giải quyết vấn đề. Nâng tầm khả năng ngoại ngữ: đọc dịch tài liệu chuyên ngành, giao tiếp thường xuyên tại Câu lạc bộ Tiếng Anh của FSOFT Academy.",
  "yeu_cau_cong_viec": "Là sinh viên đã/sắp tốt nghiệp chuyên ngành Công nghệ thông tin, Điện tử viễn thông, Cơ điện tử, Tự động hóa… hoặc các chuyên ngành có liên quan.Có kiến thức nền tảng tốt về một ngôn ngữ lập trình: Python / Java / Javascript / C++Ưu tiên ứng viên có kiến thức cơ bản về lập trình vi điều khiển và phát triển các hệ thống Nhúng (Embedded), IoT…=Có thể tham gia đào tạo / làm việc Full-time từ thứ 2 – thứ 6.Ham học hỏi, máu lửa, nhiệt huyết, sẵn sàng chinh chiến đối đầu với thử thách khó khăn tại các dự án phần mềm lớn. Tuân thủ kỷ luật & có trách nhiệm với công việc.Ưu tiên ứng viên có khả năng đọc hiểu tiếng Anh tốt.",
  "quyen_loi": "Được nhận trợ cấp đào tạo toàn khóa học lên đến 20.000.000VND/khóa tùy theo mức độ đóng góp và kết quả đào tạo.Sau đào tạo: Tham gia làm việc tại các dự án với mức thu nhập hấp dẫn tương xứng với kỹ năng và kinh nghiệm của bạn, nhận thưởng tham gia dự án và lương tháng 13, tùy theo kết quả đào tạo và làm việc. Hưởng các chính sách như: hỗ trợ mua nhà, bảo hiểm FPT care…Cơ hội phát triển bản thân và làm việc cùng các chuyên gia giỏi nhất của FPT Software và khách hàng lớn đến từ Mỹ, Canada, Hàn Quốc, Nhật Bản…Tiếp cận với những công nghệ tiên tiến hàng đầu về Kiểm thử tự động, Embedded System và Automotive, phát triển kỹ năng mềm & định hướng nghề nghiệp, tư vấn bí quyết thành công từ các chuyên gia.Trải nghiệm văn hóa đặc trưng, môi trường làm việc hiện đại bậc nhất Việt Nam tại các Campus của FPT Software.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "Công ty TNHH Volio Việt Nam",
  "mo_ta_cong_viec": "1. Phát triển các ứng dụng thuộc một trong các lĩnh vực:Chỉnh sửa hình ảnh, video, âm thanh sử dụng công nghệ cao (Machine learning, Deep Learning…)Phát triển ứng dụng văn phòng: ứng dụng ebook, bộ kit văn phòng (word, excel, powerpoint, pdf…)2. Bảo trì và phát triển các ứng dụng có trên 10 triệu người dùng3. Xây dựng thư viện cho đội kĩ thuật androidCải thiện/đề xuất các thuật toán để tối ưu quá trình xử lý ảnh Cập nhật thư viện của phòng kỹ thuật theo thời gian4. Làm việc với đội kĩ thuật, hỗ trợ của Google để nghiên cứu và phát triển các kĩ thuật mới do Google đề xuất hoặc hướng dẫn.",
  "yeu_cau_cong_viec": "– Có từ 1 năm kinh nghiệm lập trình Android trở lên– Có các dự án thực tế;– Nắm được các thành phần chính của Android;– Thành thạo xử lý giao diện– Ưu tiên ứng viên đã làm việc với kotlin;– Ưu tiên Biết cách tổ chức code, xây dựng theo mô hình MVP, MVVM, Clean Architecture",
  "quyen_loi": "– Cơm trưa, đồ uống miễn phí tại văn phòng– Vé gửi xe miễn phí– Nhân viên chính thức: lương gross + thưởng dự án– Quà các sự kiện đặc biệt: tết, 08/03, 20/10, 06/04 …– Làm từ t2 – t6, giờ làm 8h30 – 17h30 (7,5h/ngày), nghỉ lễ tết theo quy định nhà nước– Thưởng lễ tết đầy đủ.– Du lịch tối thiểu 1 lần/năm, teambuilding tối thiểu 2 lần/năm. Ngân sách 100% công ty.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "• Quản lý các quy trình ITIL tại Khối CNTT, tập trung vào mảng Hỗ trợ-Vận hành dịch vụ (Delivery Services)• Rà soát hoạt động thực hiện các quy trình, xây dựng các báo cáo phân tích, đánh giá hoạt động thực thi quy trình, kiểm tra tuân thủ• Xây dựng và cải tiến các quy trình ITIL• Đề xuất các chương trình hành động nhằm cải tiến chất lượng dịch vụ• Quản trị các công cụ ITSM",
  "yeu_cau_cong_viec": "• Có kinh nghiệm tham gia  triển khai hoạt động Quản lý chất lượng dịch vụ CNTT tại các tổ chức, đặc biệt tổ chức tài chính.• Có kinh nghiệm xây dựng, triển khai, quản lý quy trình ITIL.• Có hiểu biết về các công cụ Quản lý Quy trình cung cấp dịch vụ CNTT• Có hiểu biết về mảng Auditor, Lead Auditor• Có chứng chỉ ITIL Foundation là một lợi thế• Tốt nghiệp Đại Học chuyên nghành Công nghệ thông tin",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "• Tham gia xây dựng và phát triển các dự án.• Phát triển và cập nhật tài liệu kỹ thuật• Hỗ trợ phát triển nhóm có năng lực• Cố vấn cho thành viên cơ sở và xem lại mã của họ• Tham gia hỗ trợ dự án• Báo cáo kết quả hoạt động cho người quản lý trực tiếp",
  "yeu_cau_cong_viec": "• Nhà phát triển với hơn 2 năm kinh nghiệm Angular• Hiểu biết thành thạo về đánh dấu web, bao gồm HTML5, CSS3• Hiểu biết thành thạo về kịch bản phía máy khách và các khung JavaScript / TypeScript, bao gồm cả JQuery• Hiểu biết tốt về các thư viện và khuôn khổ SPA JavaScript / TypeScript nâng cao, chẳng hạn như ReactJS, Redux, AngularJS• Hiểu biết tốt về xử lý yêu cầu không đồng bộ, cập nhật một phần trang và AJAX• Hiểu biết thành thạo về các vấn đề tương thích trên nhiều trình duyệt và cách khắc phục chúng• Kinh nghiệm trong môi trường DevOps để triển khai mã của riêng bạn là một lợi thế",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "-Phát triển kiến trúc trang web giao diện người dùng.-Thiết kế các tương tác của người dùng trên các trang web.-Phát triển các ứng dụng trang web back-end.-Tạo máy chủ và cơ sở dữ liệu cho chức năng.-Đảm bảo tối ưu hóa đa nền tảng cho điện thoại di động.-Đảm bảo khả năng đáp ứng của các ứng dụng.-Làm việc cùng với các nhà thiết kế đồ họa cho các tính năng thiết kế web.-Nhìn xuyên suốt một dự án từ khi thai nghén đến khi thành phẩm.-Thiết kế và phát triển API.-Đáp ứng cả nhu cầu kỹ thuật và tiêu dùng.-Bám sát sự phát triển của các ứng dụng web và ngôn ngữ lập trình.",
  "yeu_cau_cong_viec": "-Bằng cấp về khoa học máy tính.-Kỹ năng tổ chức và quản lý dự án mạnh mẽ.-Thành thạo với các ngôn ngữ giao diện người dùng cơ bản như HTML, CSS và JavaScript.-Quen thuộc với các khung JavaScript như Angular JS, React và Amber.-Thành thạo với các ngôn ngữ phía máy chủ như Python, Ruby, Java, PHP và .Net.-Quen thuộc với công nghệ cơ sở dữ liệu như MySQL, Oracle và MongoDB.-Kỹ năng giải quyết vấn đề tốt.-Sự chú ý đến chi tiết.",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "-Tạo trang web hoàn chỉnh ứng dụng có thể chạy trên nhiều nền tảng.-Triển khai người dùng giao diện được thiết kế tốt và máy khách logic bằng cách sử dụng thiết kế material design nguyên tắc.-Design and phát triển web ứng dụng quy mô lớn. Tin cậy bảo mật, tính đúng đắn, bảo mật, hiệu suất, chất lượng và ứng dụng trả lời khả năng.-Làm việc với thiết kế nhóm và sản phẩm để hiểu các yêu cầu của người dùng cuối, xây dựng các trường hợp sử dụng và sau đó chuyển chúng thành công việc triển khai kỹ thuật hiệu quả.-Phát triển chất lượng web giao diện bằng cách sử dụng REST web dịch vụ.-Phát triển giao diện, thành phần và web / di động người dùng hữu ích.",
  "yeu_cau_cong_viec": "-Có kinh nghiệm làm việc ít 3 năm với JavaScript, HTML, CSS.-Có ít nhất 2-3 năm kinh nghiệm với các framework Javascript: ReactJS-Có kinh nghiệm phát triển các trang web đáp ứng, sử dụng các bộ tiền xử lý Bootstrap, Material-UI và CSS như Less và Sass.-Hiểu biết sâu sắc về JavaScript, các nguyên tắc cơ bản của ES6-Kiến thức vững chắc về HTML / CSS, JQuery-Trải nghiệm với TypeScript-Quen thuộc với Redux, React Hook Form, NextJS, React Testing Library, Server Side Rendering, (GraphQL là một điểm cộng lớn)-Hiểu biết thành thạo các công cụ kiểm soát phiên bản mã, chẳng hạn như Git và Svn.",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "-Tham mưu tư vấn và tổ chức thực hiện, triển khai các dự án, cải tiến công nghệ.-Xây dựng và quản lý các chính sách, tiêu chuẩn về kiến trúc tổng thể tại  Mcredit .-Tham gia triển khai và đảm bảo tiêu chuẩn kiến trúc được áp dụng vào các dự án/yêu cầu phát triển.-Đánh giá và cho ý kiến về các thay đổi kiến trúc trong các dự án, công việc có liên quan đến thay đổi kiến trúc.-Rà soát, đánh giá, xây dựng và chuẩn hoá các phương án cải tiến kiến trúc.-Nghiên cứu xu hướng chuyển đổi kinh doanh, xu hướng công nghệ và các giải pháp.",
  "yeu_cau_cong_viec": "-Tốt nghiệp Đại học/Cao học trở lên chuyên ngành khoa học máy tính, kỹ thuật phần mềm hoặc công nghệ thông tin.- Có kinh nghiệm quản lý đơn vị- Làm việc trong/hoặc với ngân hàng hoặc/và các tổ chức tín dụng- Tư vấn, thiết kế và xây dựng giải pháp- Tham gia phát triển phần mềm hoặc triển khai các giải pháp phần mềm",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY TNHH MTV FLOWARE VIỆT NAM",
  "mo_ta_cong_viec": "The Senior Backend Engineer (SBE) designs complex backend technology solutions, develops code, and tests and maintains new and existing systems.As part of Floware’s Infrastructure & Security team, he partners closely with development teams to define scope and requirements for reusable services with integration services and APIs, and to use appropriate technology solutions for the business.The BE is a key member of the team responsible for delivering robust solutions while defining backend standards for all development teams at Floware VN.",
  "yeu_cau_cong_viec": "3+ years of experience designing, developing, and managing RESTful APIs3+ years of experience developing in any of following core language: NodeJS/Ruby on Rails/JS or experience with relevant frameworksDemonstrated design and programming skills using NodeJS, JSON, Web Services, XML, XSLT, etc...Excellent experience in designing and implementing database systems with integrity, scalability, performance, reliability, security in mindHUGE PLUS IF YOU ARE/HAVEExcellent fullstack developerExcellent understanding of backend development best practices and standardsImpeccable leadership skills and able to drive solutionsExcellent understanding of CI/CD/CDExcellent experience designing and developing backend microservices",
  "quyen_loi": "Friendly, flexible, and fun working environmentVery attractive salary based on skills and experience100% salary during probation periodPremium Health Insurance PackagePerformance bonus up to 96 million dong or more in the yearFree office lunch, fruit, coffee, tea, snack bar everydayMonthly team activity allowanceFull income tax, insurance paid by company (Net Salary)13th month of salaryGreat opportunity for career developmentCompany trip, team building, monthly party, etc.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 11/08/2022"
},
{
  "name": "HD Saison Finance Co., Ltd",
  "mo_ta_cong_viec": "- Xử lý các sự cố kỹ thuật liên quan đến hệ thống công nghệ thông tin phát sinh cho người sử dụng tại văn phòng và các Điểm giới thiệu dịch vụ (“SIP”)- Định kỳ kiểm tra, bảo trì máy móc, đảm bảo tất cả các thiết bị vi tính tại SIP được kết nối đúng kỹ thuật và sẵn sàng để sử dụng.- Kiểm tra tín hiệu ADSL/FTTH/3G và đảm bảo hoạt động tốt ở các SIP.- Triển khai theo kế hoạch của công ty về việc mở/ hoặc đóng SIP theo yêu cầu.- Cài đặt và nâng cấp hệ thống máy tính theo đúng yêu cầu kỹ thuật.- Hỗ trợ kiểm kê thiết bị vi tính và dán mã tài sản cho các thiết bị vi tính khi có yêu cầu.- Thực hiện các nhiệm vụ khác được giao",
  "yeu_cau_cong_viec": "- Trung Cấp Công Nghệ Thông tin/ Kỹ Thuật.- Hỗ trợ kỹ thuật Windows XP/7/10, MS Office, Email, ADSL, FTTH, Lan/Wan- Giao tiếp tốt, làm việc nhóm, làm việc độc lập, có khả năng di chuyển tốt.",
  "quyen_loi": "- Làm việc trong một môi trường chuyên nghiệp, luôn không ngừng phát triển với nhiều cơ hội thăng tiến.- Thu nhập lương ổn định, phụ cấp ăn trưa, đi lại, điện thoại, thêm vào đó, bạn còn được xem xét tăng lương lương hằng năm.- Thưởng năng lực cá nhân hàng năm và cam kết khoản lương tháng 13.- Ngoài 12 ngày phép năm theo quy định luật lao động , bạn còn được hưởng thêm 3 ngày phép theo quy định Công ty và 1 ngày nghỉ Giáng sinh.- Được hưởng 100% lương trong thời gian thử việc, được đóng đầy đủ toàn bộ các chế độ bảo hiểm sau khi ký hợp đồng lao động chính thức.- Định kỳ hằng năm có tham gia chế độ chăm sóc sức khỏe cho chính bạn và được tham gia gói ưu đãi khi mua bảo hiểm tự nguyện dành cho người thân.- Tổ chức định kỳ hằng năm các hoạt động phát triển đội nhóm gắn kết nhân viên.- Tham gia các hoạt động dành cho đoàn viên, được quan tâm đến các hoạt động hỗ trợ tinh thần như hiếu hỉ, sinh nhật, thăm hỏi ốm đau, tương thân tương ái hỗ trợ vượt qua giai đoạn khó khăn v.v",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "bePOS",
  "mo_ta_cong_viec": "- Tổ chức Nhóm Kinh doanh- Duy trì những mối quan hệ kinh doanh hiện có, nhận đơn đặt hàng và thiết lập những những mối quan hệ kinh doanh mới.- Tổ chức lịch công tác hàng ngày đối với những khách hàng hiện có và thúc đẩy các khách hàng tiềm năng.- Hiểu rõ và thuộc tính năng, chức năng, giá, ưu nhược điểm của sản phẩm của bePOS và sản phẩm tương tự của đối thủ cạnh tranh.- Nắm được quy trình tiếp xúc khách hàng, quy trình xử lý khiếu nại thông tin, quy trình nhận và giải quyết thông tin khách hàng, ghi nhận đầy đủ theo các biểu mẫu của các quy trình này.- Tiếp xúc khách hàng và ghi nhận toàn bộ các thông tin của khách hàng trong báo cáo. Báo cáo nội dung tiếp xúc khách hàng trong ngày cho COO.- Gửi báo cáo KPI & đề xuất giải pháp cho BOD hàng tuần.- Nhận và xử lý các khiếu nại của khách hàng về chất lượng sản phẩm, dịch vụ, VAT (nếu có).- Đưa ra kế hoạch tổ chức hội thảo, sự kiện & thực hiện các kế hoạch này.- Giao dịch, tìm hiểu nhu cầu của khách hàng. Tìm kiếm khách hàng tiềm năng.- Cập nhật kiến thức công việc qua việc, nghiên cứu về kinh doanh và tiếp thị, Event, hội thảo, duy trì các mối quan hệ khách hàng.- Phát triển việc kinh doanh ở địa bàn được giao phó.- Chăm sóc khách hàng theo mục tiêu đã định.",
  "yeu_cau_cong_viec": "- Kinh nghiệm: 02 năm- Có kỹ năng quản lý, lập kế hoạch;- Có kỹ năng giao tiếp, xử lý tình huống tốt;- Có kinh nghiệm bán hàng mảng Công nghệ thông tin là một lợi thế.",
  "quyen_loi": "- Tổng thu nhập: > 15 triệu (Lương cứng + phụ cấp + Hoa hồng)- Phụ cấp bữa trưa 50.000/ ngày- Chế độ BH theo quy định nhà nước, bảo hiểm sức khỏe bảo việt.- Lương tháng 13- Thưởng kinh doanh hàng tháng- Chế độ xem xét tăng lương/ thăng tiến mỗi quý- Trong định hướng của bePOS có nhiều cấp độ và vị trí tương ứng cùng đãi ngộ hấp dẫn (chi tiết sẽ được chia sẻ trong buổi phỏng vấn).",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "- Tìm hiểu nghiệp vụ hệ thống nguồn- Tìm hiểu cấu trúc dữ liệu và ý nghĩa nghiệp vụ các cấu trúc dữ liệu Table/Field cũng như logic nghiệp- Xây dựng tài liệu đặc tả dữ liệu/báo cáo.- Thu thập và xây dựng tài liệu đặc tả yêu cầu người dùng- Thiết kế tài liệu Matrix Mapping (highlevel design)- Đầu mối về nghiệp vụ giữa các bên- stakeholders",
  "yeu_cau_cong_viec": "- Tốt nghiệp đại học hệ chính quy, ưu tiên các chuyên ngành CNTT, Khoa học máy tính, Hệ thống thông tin, Tin học kinh tế, Tài chính – ngân hàng.- Có khái niệm về data warehousing concepts/ Data lake (ETL, Staging/Target Area, OLAP, Dimensional Modelling, Data Marts ...)- Đã tham gia các khóa học Data online/offline một lợi thế (Ex: DataCamp, Udemy...)- Có kinh nghiệm BA làm việc trong các dự án về data warehouse/ Report/ Data Lake, Bigdata. Hoặc triển khai cá dự án lõi của cty Tài chính/ Ngân hàng LOS, Corebanking, Debt Collection …- Có kỹ năng và kinh nghiệm test là một lợi thế.- Ưu tiên các ứng viên có chứng chỉ nghề DA ở các level tương đương",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN IKAME VIỆT NAM",
  "mo_ta_cong_viec": "Xây dựng và phát triển các dự án Game mobile trên nền tảng Unity cho Android và iOSXây dựng và triển khai kiến trúc hệ thống game (game architecture design)Cùng team lên ý tưởng và giải pháp cho các tính năng mới của gameSửa lỗi và cải thiện tính năng, hiệu suất trò chơiPhối hợp với các thành viên trong team để vận hành và tối ưu hoá sản phẩmTham gia quá trình xây dựng team dev; chia sẻ và phát triển chuyên môn dev của công ty",
  "yeu_cau_cong_viec": "Thành thạo C# & UnityTối thiểu 2 năm kinh nghiệm làm Unity; hiểu biết về UI Canvas, Physic, Particle System, Optimization,…Có nền tảng tư duy thuật toán, cấu trúc giải thuật, tư duy logic tốtYêu thích làm game và chơi game; đặc biệt quan tâm tới game blockchain là một lợi thếBiết Mirror hoặc Photon là một lợi thếKhả năng tư duy, sáng tạo tốtCó trách nhiệm cao trong công việc, thái độ cầu tiến và ham học hỏi công nghệ mớiCó khả năng đọc hiểu tài liệu bằng Tiếng Anh là một lợi thế",
  "quyen_loi": "Mức lương lên tới 2000$; review lương 2 lần/ năm.Thưởng LINH HOẠT & HẤP DẪN: Thưởng nóng + Thưởng kinh doanh trích % lợi nhuận của team và của cả công ty + Thưởng Lễ + Thưởng tháng lương 13Thưởng hấp dẫn: Thưởng kinh doanh theo Qúy + Thưởng nóng + Thưởng tháng lương 13 + Thưởng LễTrợ cấp ăn trưa 1 triệu đồng/ thángCơ hội trực tiếp tham gia chinh chiến các dự án game với cơ hội học hỏi kiến thức phát triển, xây dựng sản phẩm từ CEO, Leader và các thành viên khác trong quá trình làm việc.Được tham gia các buổi đào tạo toàn diện về kỹ năng mềm và kỹ năng chuyên môn tại công tyĐược hỗ trợ xây dựng lộ trình phát triển nghề nghiệp bản thân.Môi trường làm việc năng động, sáng tạo, chuyên nghiệp.Trang thiết bị chuyên môn đầy đủ, phục vụ cho nhu cầu công việc.Các chế độ bảo hiểm, nghỉ phép, khám sức khỏe, thưởng lễ tết,… được đảm bảo cho nhân viênTham gia các hoạt động du lịch, team building, các sự kiện lớn nhỏ cùng công ty hàng năm.Thời gian làm việc: 8:30 - 18:00 từ thứ Hai tới thứ Sáu, không OTCòn gì nữa? Hãy cùng chúng mình khám phá và cùng xây dựng văn hóa iKame để phát triển từng cá nhân nhé!!",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN IKAME VIỆT NAM",
  "mo_ta_cong_viec": "Tạo Game Design Documents chi tiết cho sản phẩm từ gameplay, level design,... cho đến trải nghiệm và giao diện người dùng.Thiết kế mechanic, game rule và đảm bảo mọi thứ cân bằng một cách hợp lý.Tạo levels, missions,... để tạo trải nghiệm tốt nhất cho người chơi với lối chơi sáng tạo, gây nghiện.Xây dựng meta game và có lộ trình phát triển hợp lý.Tham gia phân tích, đánh giá, tối ưu sản phẩm theo biểu đồ.Theo dõi chỉ số, phân tích và đưa ra các action phù hợp giai đoạn dự án.Xây dựng game story (nếu có) phù hợp với mục tiêu sản phẩm và được duyệt bởi Product Manager.Cập nhật, nghiên cứu, phân tích thị trường, cung cấp prototypes để thúc đẩy các ý tưởng sáng tạo.",
  "yeu_cau_cong_viec": "Trên 2 năm kinh nghiệm thiết kế game với tối thiểu 1 năm kinh nghiệm làm sản phẩm dòng casual/mid-coreKỹ năng tư duy, sáng tạo và khả năng logic toán học tốt.Có kinh nghiệm phân tích, đánh giá và tối ưu gameYêu thích chơi game, mong muốn phát triển sự nghiệp trong ngành gameƯu tiên ứng viên có kiến thức và hiểu biết về blockchain và các sản phẩm “Play-to-earn”Ưu tiên ứng viên có kinh nghiệm nghiên cứu và phân tích thị trường (không bắt buộc)Ham học hỏi, có tư duy phát triển, cải tiến công việcCởi mở, chủ động giao tiếp, tương tác và kết hợp công việc với đồng đội.Đọc hiểu tài liệu tiếng Anh tốt là 1 lợi thế",
  "quyen_loi": "Mức lương lên tới 1500$; review lương 2 lần/ năm.Thưởng LINH HOẠT & HẤP DẪN: Thưởng nóng + Thưởng kinh doanh trích % lợi nhuận của team và của cả công ty + Thưởng Lễ + Thưởng tháng lương 13Thưởng hấp dẫn: Thưởng kinh doanh theo Qúy + Thưởng nóng + Thưởng tháng lương 13 + Thưởng LễTrợ cấp ăn trưa 1 triệu đồng/ thángCơ hội trực tiếp tham gia chinh chiến các dự án game với cơ hội học hỏi kiến thức phát triển, xây dựng sản phẩm từ CEO, Leader và các thành viên khác trong quá trình làm việc.Được tham gia các buổi đào tạo toàn diện về kỹ năng mềm và kỹ năng chuyên môn tại công tyĐược hỗ trợ xây dựng lộ trình phát triển nghề nghiệp bản thân.Môi trường làm việc năng động, sáng tạo, chuyên nghiệp.Trang thiết bị chuyên môn đầy đủ, phục vụ cho nhu cầu công việc.Các chế độ bảo hiểm, nghỉ phép, khám sức khỏe, thưởng lễ tết,… được đảm bảo cho nhân viênTham gia các hoạt động du lịch, team building, các sự kiện lớn nhỏ cùng công ty hàng năm.Thời gian làm việc: 8:30 - 18:00 từ thứ Hai tới thứ Sáu, không OTCòn gì nữa? Hãy cùng chúng mình khám phá và cùng xây dựng văn hóa iKame để phát triển từng cá nhân nhé!!",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "- Xây dựng giải pháp và lập trung các tầng xử lý trên hệ thống; DataWarehouse, Data Lake Data Model, BI, Downstream system, ....- Tích hợp tất cả các nguồn dữ liệu từ các hệ thống ứng dụng vào Data Warehouse/Data Lake.- Hỗ trợ các Đơn vị nghiệp vụ khi có nhu cầu khai thác dữ liệu từ hệ thống MIS/DW.- Thực hiện phân tích các mô hình dữ liệu, dự đoán, dự báo, báo cáo phân tích,…- Báo cáo định kỳ theo quy định hoặc theo yêu cầu của cấp quản lý trực tiếp.- Tham gia các dự án về Data Warehouse/Data Lake theo sự phân công",
  "yeu_cau_cong_viec": "- Thành thạo ngôn ngữ SQL- Có kinh nghiệm làm báo cáo trên công cụ BI (như Tableau, Power BI, Oracle BI, cognos IBM, Jasper ...)- Có khả năng lâp trình báo cáo trên nên tảng AWS, công cụ báo cáo AWS Quicksight.- Có kinh nghiệm triển khai ít nhất một dự án Data warehouse hoặc báo cáo, hoặc ETL cho Ngân hàng/Công ty tài chính.- Có kinh nghiệm phát triển ETL trên các nền tảng Oracle DI, IBM Data stage, Sap dataservices, Talend, Pentaho…..- Có kinh nghiệm với cá các công cụ tích hợp/khai thác dữ liệu trên nên tảng AWS (DMS, AWS Glue, workflow,stepFunction, lambda, anthena)- Có kiến thức về các nền tảng dữ liệu trên AWS (Amazon S3, AWS Foundation, Amazon Redshift, …)- Có kiến thức về các công nghệ đồng bộ dữ liệu AWS DMS, CDC.v.v.- Có kinh nghiệm làm việc với dữ liệu từ các nguồn ứng dụng tác nghiệp của Ngân hàng/công ty tài chính (Corebank,WAY4, ….)- Có khả năng đọc và hiểu tài liệu yêu cầu hoặc thiết kế chi tiết, phối hợp nhóm, kỹ năng trình bày.- Tốt nghiệp hệ chính quy các trường đại học trong nước hoặc nước ngoài chuyên ngành CNTT hoặc các ngành tương đương hoặc có các chứng chỉ tương đương được công nhận bởi các tổ chức uy tín;",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "Công ty Cổ phần Giải pháp Công nghệ ESCS",
  "mo_ta_cong_viec": "+ Phối hợp phân tích và lập trình xây dựng các phần mềm ứng dụng theo yêu cầu của Công ty+ Lập kế hoạch và kiểm soát tiến độ dự án phần mềm+ Nghiên cứu công nghệ mới để áp dụng vào công việc",
  "yeu_cau_cong_viec": "• Kinh nghiệm Front-end phát triển phần mềm với HTML/CSS, Mvc, JS, Jquery, Html/Css  (chấp nhận sinh viên mới ra trường),• Thành thạo các framework css như bootstrap• Nắm vững phương pháp lập trình (OOP), design pattern.• Có hiểu biết hoặc thành thạo Typescript• Có kinh nghiệm với RESTFul và APIs• Kinh nghiệm về Javascript, HTML5, CSS3• Tinh thần ham học hỏi, nghiên cứu các kỹ thuật mới• Ứng viên sinh năm từ 1995-2000",
  "quyen_loi": "Cơ hội thử thách với các dự án quy mô lớn• Cơ hội tiếp cận với các công nghệ mới, được training bởi những người nhiều kinh nghiệm• Du lịch công ty, khám sức khỏe định kỳ• Môi trường làm việc chuyên nghiệp, năng động, có cơ hội thăng tiến;• Cơ hội được tham gia phát triển các dự án số hóa trong lĩnh vực bảo hiểm, findtech• Được hưởng các chế độ BHXH, BHYT… và các phúc lợi khác theo quy định của Luật lao động và của Công ty;• Được xét tăng lương 02 lần/năm;• Lương tháng 13 và thưởng theo năng lực + thưởng dự án;• 12 ngày phép/ năm;• Lương từ 6.000.000VNĐ - 10.000.000VNĐ với sinh viên mới ra trường• Đối với các bạn có kinh nghiệm từ 1 năm trở lên thì mức lương từ 15.000.000VNĐ - 35.000.000VNĐ tuỳ vào năng lực;",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "Xây dựng báo cáo và dashboard phân tíchGiải thích các xu hướng trên các nguồn dữ liệu, các cơ hội tiềm năng để tăng trưởng hoặc cải tiến và những thông tin mới cho descriptive data analysisPhát triển và giám sát các dự án quy mô vừa và nhỏ. Phân tích các chỉ số đo lường để liên tục cải tiến các sản phẩm.",
  "yeu_cau_cong_viec": "Biết sử dụng SQL trong datawarehouse (native SQL) và trong các công cụ BI (Tableau, PowerBI..)Biết code Python là điểm tốtCó kĩ năng giao tiêp và cộng tác chủ độngCó kỹ năng tự quản lý công việc bản thân, báo cáo một cách chủ độngTư duy về thống kê và phân tíchCó kinh nghiệm trước đó trong vai trò phân tích hoặc trình độ học vấn tại các ngành Công nghệ thông tin, Khoa học máy tính, Tài chính, hoặc các ngành tương đương",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng tháng lương thứ 13,...• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "VUIHOC.vn",
  "mo_ta_cong_viec": "Phát triển hệ thống website của công tyXây dựng hệ thống API cho Mobile App, Web App, sử dụng Node.js, MySql, Mongo, KafkaPhát triển các sản phẩm về giáo dục trực tuyến của công tyHỗ trợ giải quyết các vấn đề của dự ánLàm việc, phối hợp công việc theo nhóm dưới sự phân công công việc của quản lý dự án.",
  "yeu_cau_cong_viec": "Độ tuổi: 22-29• Có thể làm việc độc lập cũng như làm việc teamwork tốt. Tham gia xây dựng giải pháp cho hệ thống 100k+ người dùng• Có kiến thức tốt về lập trình hàm, lập trình hướng đối tượng, có thể hiểu và áp dụng các design pattern• Thành thạo ngôn ngữ  lập  trình  PHP, có kinh nghiệm làm việc với  Laravel hoặc Yii Framework• Ưu tiên ứng viên có kinh nghiệm làm việc NodeJS, ExpressJS, VueJS, jQuery• Thành thạo làm việc với cơ sở dữ liệu quan hệ như MySQL, Postgres; Có kinh nghiệm tối ưu hóa truy vấn là một lợi thế.• Ưu tiên ứng viên có thể làm việc với Linux; Sử dụng tốt các công cụ lập trình, công cụ git; Ưu tiên ứng viên có hiểu biết về các phương pháp bảo mật cơ bản, thực hiện tối ưu hóa",
  "quyen_loi": "Ký Hợp đồng lao động và các chế độ bảo hiểm theo luật lao độngLương tháng thứ 13, xét tăng lương 1 năm 2 lần, nghỉ phép có lương 12 ngày/nămĐược hỗ trợ tham gia Hội thảo, Seminar các khóa đào tạo nâng cao kỹ năng bản thân theo yêu cầu công việcTrải nghiệm làm việc trên các hệ thống lớn, giúp nâng cao các kỹ năng, kinh nghiệm lập trình.• Thu nhập cạnh tranh• Các hoạt động Teambuilding hàng quý và cuối năm,• Có cơ hội được làm việc với các hệ thống lớn, CCU cao.• Được đào tạo bài bản từ những anh/chị có chuyên môn cao trong lĩnh vực• Môi trường làm việc chuyên nghiệp, đảm bảo sự thoải mái, tự do sáng tạo.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/08/2022"
},
{
  "name": "Công ty cổ phần sáng tạo và tích hợp công nghệ cao I&I",
  "mo_ta_cong_viec": "Xây dựng & Phát triển các website, landing page sản phẩm của công ty bao gồm phát triển các tính năng mới, update PSD -> Wordpress.Khắc phục những vấn đề xảy ra trong quá trình vận hành.Thực hiện lập trình theo sự phân công task của Teamleader.Vận hành quản trị Server, Linux, Kubernetes,...Kết hợp với các thành viên khác để apply cấu hình vào hệ thống",
  "yeu_cau_cong_viec": "Không yêu cầu kinh nghiệmCó kiến thức về cấu trúc và cơ chế hoạt động của WordPress.Nắm vững về các chuẩn viết code cho WordPress, về PHP (biết sử dụng Composer), về CSS/JavaScript.Có kiến thức về React, Flutter, SEO, TMĐT là một lợi thế.",
  "quyen_loi": "Được hỗ trợ lương từ 3.000.000 - 5.000.000đ/tháng.Được công ty đóng 100% BHXH, BHYT.Du lịch, team building và đào tạo kỹ năng.Được làm việc trong môi trường năng động, chuyên nghiệp, đãi ngộ xứng đáng với năng lực và hiệu quả công việc",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN VIỆN MẮT QUỐC TẾ VIỆT - NGA",
  "mo_ta_cong_viec": "• Quản trị mạng internet•\tQuản tri hệ thống camera•\tQuản lý máy in đen trắng, máy in màu.•\tTriển khai lắp đặt hệ thống mạng mới , Lắp đặt hệ thống cho các phòng ban mới.•\tSửa chữa, khắc phục sự cố về máy in, máy tính, mạng Lan và internet, camera(Công việc cụ thế chi tiết sẽ trao đổi thêm khi phỏng vấn)•\tCấu hình, cài đặt hệ điều hành, phần cứng máy tính, máy in.•\tCấu hình, cài đặt mạng máy tính, Wifi cơ bản: Ưu tiên có kinh nghiệm làm việc với các Router Draytek, Mikrotik, …•\tCấu hình, cài đặt hệ thống Camera IP: Hikvision, Dahua,…•\tCấu hình, cài đặt điện thoại IP Yealink hoặc GrandStream,…•\tBáo cáo công việc với Trưởng phòng",
  "yeu_cau_cong_viec": "Từ trung cấp trở lênƯu tiên khối CNTTKinh nghiệm: Từ 2 – 3 năm kinh nghiệm, nhanh nhẹn, gắn bó.",
  "quyen_loi": "Lương từ 8 - 10 triệu (tùy thuộc vào năng lực)Làm việc trong môi trường năng độngHưởng đầy đủ các chế bộ BHXHĐịa chỉ: 789 Nguyễn Văn Linh, Phường Vĩnh Liệm, Lê Chân, Hải Phòng",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/09/2022"
},
{
  "name": "FPT Software",
  "mo_ta_cong_viec": "FPT Software Hà Nội cần tuyển 50 Lập trình viên C/Embedded tham gia Chương trình đào tạo tân binh và làm việc trực tiếp tại các dự án hàng đầu trong lĩnh vực Automative – phát triển công nghệ cho xe hơi thông minh hạng sang (Tham gia phát triển các phần mềm Nhúng cho hệ thống điều khiển, kiểm soát an toàn cho xe hơi, hệ thống thông tin giải trí trong ô tô (media, video, audio), hệ thống định vị và dẫn đường (navigation), phát triển Middleware drivers cho các hệ thống GPS, Radio (AM/FM), Digital Radio (DAB/MDB), Bluetooth, Wifi…) và tham gia phát triển platform cho các thiết bị IoT.Chương trình đào tạo tân binh Fresher C/ Embedded là chương trình được xây dựng nhằm giúp các tân binh của FPT Software có cơ hội tìm hiểu và hệ thống lại các kiến thức C/ Embedded và học hỏi quy trình phát triển phần mềm trước khi tham gia vào các dự án thực tế trong lĩnh vực Automative. Nội dung khóa học bao gồm các phần:Lập trình CLàm việc với ngôn ngữ lập trình C, thao tác file, con trỏ, sử dụng structure, hiểu cấu trúc dữ liệu và giải thuật.Làm việc với Linker Script, Macro Bit Byte Operation, Unit testing.Làm việc với GIT, tránh các lỗi common defect trong lập trình C.Lập trình NhúngLập trình nhúng với: Embedded Software Development, Getting Started with KL46 freedom board.Làm việc với: ARM Cortex-M architecture, ARM Cortex-M Exception & InterruptLàm việc với: Peripherals Timer, Peripherals UART, Basic RTOS Concepts.Phát triển phần mềm theo quy trình chuyên nghiệpHiểu các bước thực hiện dự án, bao gồm thiết kế ứng dụng, làm GUI, thiết kế code, thực hiện Unit test, kiểm tra chất lượng dự án.Luyện tập kỹ năng code trong dự án.Rèn luyện các kỹ năng mềm: Viết email, kỹ năng phỏng vấn, thuyết trình, kỹ năng phân tích giải quyết vấn đề. Nâng tầm khả năng ngoại ngữ: đọc dịch tài liệu chuyên ngành, giao tiếp thường xuyên tại Câu lạc bộ Tiếng Anh của FSOFT Academy.",
  "yeu_cau_cong_viec": "Là sinh viên đã/sắp tốt nghiệp chuyên ngành Công nghệ thông tin, Toán tin, Khoa học máy tính, Kỹ thuật phần mềm, Điện tử viễn thông, Cơ khí, Cơ điện tự, Tự động hóa… hoặc các chuyên ngành có liên quan.Yêu thích và đam mê làm việc với lập trình C. Ưu tiên ứng viên có kiến thức cơ bản về lập trình vi điều khiển và phát triển các hệ thống Nhúng (Embedded), IoT…Có thể tham gia đào tạo/làm việc Full-time từ thứ 2 – thứ 6.Ham học hỏi, máu lửa, nhiệt huyết, sẵn sàng chinh chiến đối đầu với thử thách khó khăn tại các dự án phần mềm lớn. Tuân thủ kỷ luật & có trách nhiệm với công việc.Ưu tiên ứng viên có khả năng đọc hiểu tiếng Anh tốt.",
  "quyen_loi": "Được nhận trợ cấp đào tạo toàn khóa học lên đến 20.000.000VND/khóa tùy theo mức độ đóng góp và kết quả đào tạo.Sau đào tạo: Tham gia làm việc tại các dự án với mức thu nhập hấp dẫn tương xứng với kỹ năng và kinh nghiệm của bạn, nhận thưởng tham gia dự án và lương tháng 13, tùy theo kết quả đào tạo và làm việc. Thu nhập trung bình từ 12-16M/tháng. Hưởng các chính sách như: hỗ trợ mua nhà, bảo hiểm FPT care…Cơ hội phát triển bản thân và làm việc cùng các chuyên gia giỏi nhất của FPT Software và khách hàng lớn đến từ Mỹ, Hàn Quốc, Nhật Bản…Tiếp cận với những công nghệ tiên tiến hàng đầu về Embedded System và Automotive, phát triển kỹ năng mềm & định hướng nghề nghiệp, tư vấn bí quyết thành công từ các chuyên gia.Trải nghiệm văn hóa đặc trưng, môi trường làm việc hiện đại bậc nhất Việt Nam tại các Campus của FPT Software.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "Splus Software",
  "mo_ta_cong_viec": "Implement code/implement functions of .NET system/application.Use C#/Net programming language on the Windows platform to implement.Using PHP/Java languages to build websites is an advantage.Conduct Unit tests, write technical specs, and design documents.Analyze and design the flow of processing functions of the systemPerform bug fixes for functions designed, coded/implemented.Writing software installation/deployment documentation; software manuals.Perform other tasks as assigned by superiors.",
  "yeu_cau_cong_viec": "Experience in real projects ( WE ARE OPENING FOR FRESHER)Knowledge of programming languages .NET (C), C#, OOP.Having knowledge and understanding of software production process, and outsourcing.Knowledge and experience in using Entity Framework, MVC is a plus.Interesting in working in the software outsourcing environment and in the Japanese market.Being able to use Japanese is an advantage in negotiating a better salary.",
  "quyen_loi": "- Working in a fast-paced, professional atmosphere with several prospects for advancement.- The corporation gives every staff with a LAPTOP.- Following the probationary time, the firm pays for social insurance, health insurance, and unemployment insurance.- Become a member of the 24-hour health and accident insurance package (according to the working age)- Receive perks commensurate with working seniority.- Sponsored studies in foreign languages, professional certifications (ISTQB, PMP, AWS...), and soft skills.- Opportunity to visit SPLUS JAPAN ONSITE (requires Japanese level of N3 or higher).- Evaluation of performance twice a year- Football, English, and Japanese clubs- Annual company vacation, quarterly team-building exercises, monthly birthday celebrations for workers, and other events throughout the year (March 8, October 20, Mid-Autumn Festival, Christmas ...)- Annual vacation: 12 days of paid time off plus the Company's birthday (November 27).- TET bonus (1-3 months pay) based on job performance and the company's financial status.* Hours of operation: 9:00-18:00* Work environment: flexible (You can work from home, or go to the office)",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/08/2022"
},
{
  "name": "CÔNG TY TNHH RABILOO",
  "mo_ta_cong_viec": "- Nghiên cứu và phân tích yêu cầu dự án.- Lập kế hoạch Test, thiết kế Test Case, chạy Test Case.- Theo dõi, tổng hợp, đánh giá và báo cáo kết quả Test cho các bên liên quan.- Xây dựng quy trình, tài liệu test phần mềm- Là cầu nối giữa khách hàng và bộ phận lập trình- Hỗ trợ khách hàng vận hành sản phẩm",
  "yeu_cau_cong_viec": "- Có ít nhất 1 năm kinh nghiệm ở vị trí tương đương- Thành thạo testcase, SQL và test API- Có hiểu biết về quy trình phần mềm và có khả năng xây dựng quy trình test- Khả năng đọc - hiểu và phân tích yêu cầu dự án- Biết sử dụng các tool quản lý bug.- Yêu thích công việc, ham học hỏi, có tinh thần trách nhiệm cao, tỷ mỷ, cẩn thận.- Có khả năng training intern hoặc fresher- Ưu tiên ứng viên có kinh nghiệm làm Automation Test- Ưu tiên ứng viên biết tiếng Nhật hoặc có chứng chỉ ISTQB",
  "quyen_loi": "- Mức lương cạnh tranh theo năng lực và kinh nghiệm- Thưởng dự án, tháng 13+ (trung bình 14 15 tháng lương/năm) và các dịp Lễ, Tết, sinh nhật- Môi trường trẻ, năng động, có nhiều cơ hội phát triển bản thân.- Được đào tạo về kỹ năng công nghệ, các kỹ năng mềm, các kỹ năng quản lý dự án,…- Được tham gia lớp học tiếng Nhật miễn phí tại công ty (học 02 buổi /tuần sau giờ hành chính)- Được học hỏi những kiến thức mới như BigData, AI, NLP, chatbot, xử lý hình ảnh- Có cơ hội onsite ngắn hạn hoặc dài hạn tại Nhật- Xét duyệt tăng lương theo kết quả làm việc 3 tháng/lần- Được hưởng nghỉ phép bắt đầu từ thử việc và không dùng hết được trả lại tiền lương- Khám sức khỏe định kỳ 1 năm 1 lần- Hưởng bảo hiểm sức khỏe dành riêng cho nhân viên Rabiloo- Thưởng 1 tháng lương ngay khi nghỉ thai sản- Hưởng đầy đủ các chế độ theo quy định pháp luật (BHXH, BHYT, BHTN) và công ty (nghỉ mát, team building, sinh nhật,…)- Được tham gia vào các nhóm, câu lạc bộ bóng đá, game của công ty- Phúc lợi ốm đau, thai sản, hiếu hỉ cho cả người thân",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "Vega Corporation",
  "mo_ta_cong_viec": "Tiếp nhận các yêu cầu về sản phẩm, dịch vụ đối với các sản phẩm Fintech;Thực hiện nghiệp vụ phân tích, làm rõ yêu cầu và thống nhất với các bên liên quan;Xây dựng các tài liệu phân tích, đặc tả yêu cầu, mô hình hoá quy trình nghiệp vụ;Tham gia, giám sát quá trình kiểm thử nhằm đảm bảo chất lượng của hệ thống đáp ứng đúng và đủ các yêu cầu đã đặt ra;Quản lý các nội dung điều chỉnh của sản phẩm, phân tích mức độ ảnh hưởng của các điều chỉnh đối với tổng thể hệ thống.",
  "yeu_cau_cong_viec": "Có trên 1 năm kinh nghiệm trong công tác phân tích nghiệp vụ;Từng tham gia phân tích/ xây dựng quy trình/ kinh doanh sản phẩm của các công ty tài chính, cổng thanh toán/ví, ngân hàng là một lợi thế;Ưu tiên ứng viên có kiến thức tổng quan về tài chính, ngân hàng;Kỹ năng mô tả bằng BPMN, Use-Case, Prototype;Kinh nghiêm/ khả năng làm UI/UX là một lợi thế;Có kinh nghệm làm việc với các dự án theo quy trình Agile/Scrum;Tư duy logic tốt;Khả năng giao tiếp tốt, viết tài liệu, truyền đạt tốt;Quyết liệt, tập trung làm rõ các yêu cầu không tường minh;Tinh thần ham học hỏi, trách nhiệm cao, có khả năng làm việc nhóm.",
  "quyen_loi": "Chế độ:Được review lương : 2 lần/năm;Thưởng theo năng lực và hiệu quả công việc;Đóng Bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp theo luật bảo hiểm;Được tham gia bảo hiểm sức khỏe PVI care;Ngày phép: 12 ngày/năm được hưởng nguyên lương (Ngoài các ngày nghỉ lễ theo lịch nhà nước, nghỉ hiếu hỉ, ma chay);Du lịch hàng năm, Teambuilding cuối năm do công ty tổ chức;“Happy Friday” thứ 6 hàng tuần.Được tham gia các CLB (Bóng đá, cầu lông...) và các hoạt động phong trào do Công ty tổ chức: Sinh nhật Công ty, 20/10, 8/3, Men's Day, Gala cuối năm…Hỗ trợ:Hỗ trợ ăn trưa: 500.000/tháng;Hỗ trợ nhà ở (với mỗi năm thâm niên làm việc được cộng thêm 100.000/tháng);Môi trường làm việc:Môi trường làm việc trẻ trung năng động;Không gian làm việc đẹp, chuyên nghiệp, kích thích sự sáng tạo;",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "TỔNG CÔNG TY MÁY ĐỘNG LỰC VÀ MÁY NÔNG NGHIỆP VIỆT NAM - CTCP",
  "mo_ta_cong_viec": "Giám sát và bảo trì hệ thống máy tính cũng như hệ thống mạng nội bộ của công ty, đảm bảo các thiết bị máy móc luôn trong tình trạng sử dụng tốt: desktop, laptop,IP phone, network printer, camera, máy quét vân tay.Cài đặt, nâng cấp phần mềm và hệ điều hành Windows cho máy tính người dùng.Hỗ trợ người dùng và khắc phục các vấn đề về Intranet/Internet, Email, MS Office, softphone và các phần mềm IT khác.Cấp phát và thu hồi tài khoản email, domain, và các tài khoản truy nhập hệ thống khác.Các nhiệm vụ khác theo sự phân công của Quản lý.Tuân thủ qui trình CNTT về quản lý hệ thống máy tính.",
  "yeu_cau_cong_viec": "Tốt nghiệp các trường, trung tâm đào tạo về chuyên ngành quản trị mạng, hệ thống.Nắm vững về hệ thống phần cứng máy vi tính, có kinh nghiệm xử lý các trục trặc về phần cứng máy tính (máy tính để bàn và máy tính xách tay).Cài đặt cấu hình và sử dụng thành thạo hệ thống phần mềm: hệ điều hành thông thường, hệ điều hành server, phần mềm tiện ích, ứng dụng văn phòng.Nắm vững các khái niệm về hệ thống mạng máy tính, có kinh nghiệm về việc lắp đặt, vận hành, giám sát và quản trị hoạt động của mạng LAN và các kết nối internet (LAN, ADSL, cáp quang...).Nắm vững về hệ điều hành Window và Linux.Có khả năng tự tìm tòi học hỏi, yêu thích và đam mê ứng dụng các công nghệ mới.Có tinh thần làm việc nhóm, có trách nhiệm trong công việcƯu tiên ứng viên có kinh nghiệm.",
  "quyen_loi": "Chế độ phúc lợi:· Chế độ bảo hiểm đầy đủ.· Ngày lễ nghỉ phép hằng năm.· Lương thưởng quí, ngày lễ tết...· Du lịch và teambuilding hằng năm.· Được xét năng lực và tự ứng tuyển ở vị trí cao hơn.· Chế độ phúc lợi đầy đủ cho các bạn (sinh nhật, ma chay, hiếu hỉ...).- Điều kiện làm việc:· Được đào tạo, hướng dẫn theo quy trình chuyên nghiệp",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 11/08/2022"
},
{
  "name": "CÔNG TY TÀI CHÍNH TRÁCH NHIỆM HỮU HẠN MB SHINSEI",
  "mo_ta_cong_viec": "Phân tích/thực hiện/kiểm soát thiết kế và phát triển các  giải pháp kỹ thuật , tiêu chuẩn an ninh thông tin và các biện pháp kiểm soát đảm bảo an toàn, giảm thiểu rủi ro cho các dịch vụ IT của tổ chứcKiểm soát / thiết kế triển khai các giải pháp kỹ thuật, các tiêu chuẩn bảo mật và các biện pháp để đảm bảo an toàn / giảm thiểu rủi ro cho các dịch vụ công nghệ thông tin.Quản lý sự cố An toàn thông tin trên toàn hệ thống CNTTQuản trị các thiết bị, hệ thống, dịch vụ an ninh bảo mật như IPS, Endpoint, WAF, ATP, SIEM…./ Managing equipments, systems, security services as IPS, Endpoint, WAF, ATP, SIEM….Giám sát việc triển khai, tích hợp và cấu hình của tất cả các giải pháp bảo mật mới và của bất kỳ cải tiến, thay đổi các giải pháp bảo mật hiện tại nhằm phù hợp với tiêu chuẩn bảo mật của tổ chứcPhân tích, xây dựng các phương án khắc phục sự cố an ninh thông tin và là thành viên tham gia xử lý khi có sự cố An toàn thông tin.",
  "yeu_cau_cong_viec": "Tốt nghiệp đại học chính quy trong lĩnh vực CNTT, Học viện Kỹ thuật Mật mã học / Đại học Bách khoa Hà Nội/ Đại học Công nghệ (Đại học Quốc Gia HN) hoặc tương đương.Ưu tiên có các chứng chỉ như CHFI, CSFA, CFCE, MCITP,…/Preferred Certification: CHFI, CSFA, CFCE, MCITP,…Từ 3-5 năm kinh nghiệm chuyên môn.Có hiểu biết tốt về các tiêu chuẩn bảo mật nội bộ , có định hướng tốt về công nghệ, có hiểu biết rộng rãi về các công nghệ trong an ninh thông tinCó kiến thức sâu rộng về mạng, nền tảng máy chủ (UNIX, AIX, Windows), cơ sở dữ liệu và các công nghệ bảo mật điện toán đám mây.Có hiểu biết về các tiêu chuẩn bảo mật sau: ISO 27001, PCI DSS, ITIL…//Knowledgeable about information security standards such as ISO 27000, PCI DSS, ITIL…Hiểu và phối hợp các đơn vị khác trong công ty để thực hiện công việc. Có khả năng hướng dẫn, kiểm soát lại các thao tác đơn giản trong quy trình",
  "quyen_loi": "• Thời gian làm việc: T2-T6, nghỉ T7 và CN• Lương hấp dẫn (mức lương & thưởng cạnh tranh)• Phụ cấp tăng ca, thưởng dự án, thưởng vượt chỉ tiêu, thưởng + lương tháng 13• Được công ty thực hiện đầy đủ nghĩa vụ về bảo hiểm; thai sản, con nhỏ, cưới hỏi, sinh nhật,...• Được tham gia các hoạt động teambuilding, du lịch, các hoạt động thể thao, các hoạt động xây dựng tinh thần đồng đội.• Định kỳ xét tăng lương 2 lần/năm hoặc đột xuất theo đánh giá.Đặc biệt:• Thử việc 100% lương• Bảo hiểm sức khoẻ MIC, chương trình vay ưu đãi đối với CBNV...• Thưởng theo kết quả kinh doanh hàng năm của công ty (Thường được thưởng 2 tháng lương) .• Được cử tham gia các khóa đào tạo mới, đào tạo nâng cao phù hợp với năng lực và nguyện vọng.• Môi trường chuyên nghiệp sử dụng phương pháp Scrum và agile vào quản lý phát triển sản phẩm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "SIMSTECH",
  "mo_ta_cong_viec": "Startup SIMSTECH tìm bạn đồng hành,Tham gia phát triển ứng dụng web và mobile cho lĩnh vực giáo dục và e-commerce, sử dụng JavaScript, ReactJS, React Native, Nodejs/PHP.Phát triển và nâng cấp hệ thống để thích ứng với các yêu cầu kinh doanh mới.Tham gia vào các hoạt động quy trình phát triển phần mềm.Tham gia vào các hoạt động hỗ trợ và chia sẻ kiến thức cho thành viên mới.Tiến hành kiểm thử các chức năng đã được phát triển.Thực hiện các hoạt động bảo trì cho các chương trình mới và hiện có.",
  "yeu_cau_cong_viec": "Có nền tảng vững chắc về Khoa học máy tính hoặc lập trìnhCó kỹ năng tiếng Anh là một lợi thế​​Có kiến thức cơ bản về ngôn ngữ lập trình như JavaScript, ReactJS/React Native, Nodejs/PHPCó kiến thức cơ bản về RESTful APIĐam mê xây dựng sản phẩm và dịch vụ công nghệ, giúp mọi người học hỏi và chia sẻ kiến thức.",
  "quyen_loi": "Lương thỏa thuận theo đúng năng lực và cơ hội trở thành core-member của công tyReview lương hai lần một nămĐược đào tạo/bổ trợ các kỹ năng sau- Kỹ năng chuyên môn (frontend, backend, server)- Tiếng Anh- Kiến thức về quy trình phát triển phần mềm (Agile)Giờ làm việc linh hoạt (9:00 - 18:00, Thứ Hai đến Thứ Sáu)Làm việc tại một trong những co-working space hiện đại – tiện nghi, trung tâm quận Cầu GiấyMiễn phí cà phê, trà và nước uống tại khu làm việcHỗ trợ ăn trưaMiễn phí gửi xe máy",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty Cổ phần Tự động hóa và Robotics Aubot",
  "mo_ta_cong_viec": "• Sáng từ 8h00 – 12h00; Chiều từ 13h30 – 17h30 (8h/ngày)• Từ thứ 2 đến thứ 7 hàng tuần (có thể được nghỉ một số ngày thứ 7 trong tuần, vẫn hưởng nguyên lương).•\tTham gia nghiên cứu và phát triển giải pháp quản lý và điều khiển xe tự hành, xe thông minh; quản lý kho thông minh.•\tPhát triển hệ thống phân tán đa dạng nền tảng (desktop/web).•\tPhát triển và bảo trì hệ thống, các sản phẩm liên quan đến IT.",
  "yeu_cau_cong_viec": "* Kiến thức:•\tThành thạo hoặc lập trình vững với ít nhất một trong các ngôn ngữ Java, Python, C++.•\tCó kinh nghiệm hoặc từng làm việc với cơ sở dữ liệu PostgreSQL, Microsoft SQL Server•\tCó có kiến thức về mạng và lập trình giao tiếp thiết bị với một số công nghệ: Java Socket, Java MQTT...•\tLàm việc được cơ bản với môi trường hệ điều hành Linux.•\tCó kinh nghiệm hoặc từng làm việc với open source là một lợi thế.•\tCó kinh nghiệm làm việc với AWS là một lợi thế.•\tBiết sử dụng tool quản lý version Git.* Kỹ năng:•\tKỹ năng đọc hiểu tài liệu Tiếng Anh chuyên ngành.•\tKỹ năng phân tích nghiệp vụ tốt hoăc tương đối.•\tKỹ năng lập trình clean và optimize code, có thể vận dụng design pattern là một lợi thế.",
  "quyen_loi": "• Mức lương: từ 9 triệu – 20 triệu/tháng (có thể thỏa thuận theo năng lực);• Phụ cấp ăn trưa: 30.000đ/ngày.• Công ty đóng đầy đủ BHXH, BHYT, BHTN theo quy định;• Được nghỉ 12 ngày phép hàng năm và theo quy định của pháp luật;• Được thưởng 01/01; 30/4&01/5; 02/9; Tết Trung thu, Thiếu nhi; Sinh nhật; Teambuilding, Du lịch,... và Tháng lương thứ 13.• Môi trường làm việc trẻ trung, năng động, sáng tạo và thoải mái;• Được đào tạo và nâng cao trình độ chuyên môn;• Có cơ hội thăng tiến và phát triển bản thân.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 11/08/2022"
},
{
  "name": "Công Ty TNHH Luxstay Việt Nam",
  "mo_ta_cong_viec": "- Integration of user-facing elements developed by front-end developers with server side logic- Writing reusable, testable, and efficient code- Design and implementation of low-latency, high-availability, and performant applications- Implementation of security and data protection- Integration of data storage solutions (databases, key-value stores, blob stores, etc.)",
  "yeu_cau_cong_viec": "- 1+ years in project development- Strong proficiency with JavaScript (CoffeeScript depending on your technology stack)- Knowledge of Node.js and frameworks available for it such as Express, StrongLoop, etc)- Understanding the nature of asynchronous programming and its quirks and workarounds- Good understanding of server-side templating languages (Jade, EJS, etc)- Good understanding of server-side CSS preprocessors (Stylus, Less, etc)- Basic understanding of front-end technologies, such as HTML5, and CSS3- Understanding accessibility and security compliance- User authentication and authorization between multiple systems, servers, and environments- Integration of multiple data sources and databases into one system- Understanding fundamental design principles behind a scalable application- Understanding differences between multiple delivery platforms, such as mobile vs. desktop, and optimizing output to match the specific platform- Creating database schemas that represent and support business processes- Implementing automated testing platforms and unit tests- Proficient understanding of code versioning tools, such as Git",
  "quyen_loi": "- Salary: 20-40M- Package: 14 salary months + Project bonus (If any) + Extra package: 16M/year- Young and dynamic working environment.- Continuous development of hard and soft skills through work and professional trainings.- Opportunity to approach newest technology trends- Exciting leisure: sport and art events (football club, family day…)- Company’s labor policy completely pursuant to Vietnamese labor legislation plus other benefits offered by the company (Company trip, Holiday, etc.)",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công ty Cổ phần Bán lẻ Kỹ thuật số FPT",
  "mo_ta_cong_viec": "- Cài đặt ứng dụng và phần mềm cho các dòng ĐTDĐ/Laptop.- Tư vấn, hỗ trợ cho khách hàng về kỹ thuật và chức năng của sản phẩm.- Tiếp nhận và xử lý các trường hợp bảo hành liên quan đến phần mềm sản phẩm...- Hỗ trợ nhân viên bán hàng về kỹ thuật.- Lưu ý: Thời gian làm việc: Ca xoay (Ca 1: 8h00 – 15h00/ Ca 2: 15h00 – 22h00).",
  "yeu_cau_cong_viec": "- Nam cao 1m65 trở lên, nữ cao 1m53 trở lên. tuổi từ 18 – 27.- Tốt nghiệp THPT trở lên.- Rành về kiến thức sản phẩm, am hiểu các hệ điều hành điện thoại, laptop.- Yêu thích công nghệ, ham học hỏi, chịu khó tìm tòi cập nhật kiến thức công nghệ mới.- Ngoại hình ưa nhìn, giọng nói rõ ràng, dễ nghe.- Kỹ năng giao tiếp tốt, năng động, vui vẻ và thân thiện.",
  "quyen_loi": "- Làm việc tại công ty hàng đầu Việt Nam, luôn không ngừng phát triển với nhiều cơ hội thăng tiến bản thân.- Được đào tạo chuyên nghiệp, hoàn toàn miễn phí trước khi làm việc.- Môi trường làm việc trẻ, năng động và thân thiện.- Tham gia đầy đủ các chế độ BHYT, BHXH, BHTN.- Thu nhập hấp dẫn, phù hợp năng lực bản thân.- Lương tháng 13 và thưởng theo hiệu quả kinh doanh.- Khám sức khỏe định kỳ.- Thường xuyên tổ chức các chương trình hội thao, hội diễn văn nghệ, tân niên, tất niên…",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công Ty TNHH Luxstay Việt Nam",
  "mo_ta_cong_viec": "• Collaborating with management, departments and customers to identify end-user requirements and specifications• Producing efficient and elegant code based on requirements• Testing and deploying programs and applications• Troubleshooting, debugging, maintaining and improving existing software• Compiling and assessing user feedback to improve software performance• Observing user feedback to recommend improvements to existing software products• Developing technical documentation to guide future software development projects",
  "yeu_cau_cong_viec": "• 1 year of working experience in Magento (Preferably Magento Commerce, Magento Cloud)• Hands-on experience with Magento 2.4.* is a plus.Soft-skills:- Possible to co-work with team.- Good English skills, including the ability to convey information to non-technical colleagues in a concise and clear way.Bonus points:- Experienced with Design pattern, SOLID principle- Experienced with SCRUM, GIT, SVN, REDMINE, JIRA- Fluent Spoken English- Team leadership and project management experience",
  "quyen_loi": "- Package: 14 salary months + Project bonus (If any) + Extra package: 16M/year- Young and dynamic working environment.- Continuous development of hard and soft skills through work and professional trainings.- Opportunity to approach newest technology trends- Exciting leisure: sport and art events (football club, family day…)- Company’s labor policy completely pursuant to Vietnamese labor legislation plus other benefits offered by the company (Company trip, Holiday, etc.)",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "TRUNG TÂM GIÁO DỤC NGHỀ NGHIỆP SÀI GÒN",
  "mo_ta_cong_viec": "Xây dựng kế hoạch Marketing, kinh doanh tổng thể theo tháng, quý, năm cùng phòng kinh doanh và ban giám đốc.Tham gia lên kế hoạch, triển khai chạy Ads (google, facebook, zalo….)Phân tích thị trường, ngành nghề, đối thủ cạnh trạnhHỗ trợ triển khai các công việc liên quan đến SEOLên ý tưởng, sản xuất nội dung truyền thông (bài biết, idea video / hình ảnh,…) trên các nền tảng Social MediaQuản trị nội dung Website, Fanpage.",
  "yeu_cau_cong_viec": "Có ít nhất 1 năm kinh nghiệm trong ngành Marketing.Có kinh nghiệm chạy Ads (Fb, Google, Zalo….)Hiểu biết về SEOCó khả năng lên ý tưởng tiếp thị và nghiên cứu công cụ Marketing mớiTỉ mỉ, chi tiết, có kỹ năng phân tích và tổng hợpThành thạo tin học văn phòngĐiểm cộng: Biết sử dụng PTS, thiết kế cơ bản, Đã từng triển khai dự án lớn.",
  "quyen_loi": "Thưởng các dịp lễ, tếtNguồn lực nhân sự trẻ, hòa đồng, vui vẻ, cởi mở, tranh luận giải quyết vấn đề rất tốtCông ty đang trong giai đoạn phát triển, tương lai mở rộng thêm nhiều chi nhánh nên cơ hội thăng tiến cao.Được tham gia đầy đủ chế độ BHXH theo luật định.Lương Tháng 13Địa chỉ làm việc: TRUNG TÂM DẠY NGHỀ LÁI XE SÀI GÒN – K2_Khu liên kế K2, Đường N4, Bửu Long, Biên Hòa, Đồng Nai.Địa chỉ làm việc:TRUNG TÂM GIÁO DỤC NGHỀ NGHIỆP SÀI GÒN- số 498, đường Huỳnh Văn Lũy, P. Phú Mỹ, Thủ Dầu Một, Bình Dương.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "Công ty TNHH Okono Việt Nam",
  "mo_ta_cong_viec": "1. Tham gia xây dựng kế hoạch Marketing của công ty- Đề xuất ý tưởng xây dựng kế hoạch marketing ngắn hạn và dài hạn- Nghiên cứu thị trường, đối thủ cạnh tranh2. Xây dựng và triển khai kế hoạch Marketing offlne theo tháng/quý/năm- Đưa ra ý tưởng, xây dựng kế hoạch chi tiết các kênh Marketing offline sẽ sử dụng trong từng giai đoạn- Lên kế hoạch sử dụng ngân sách theo từng giai đoạn- Quản lý, giám sát việc thực hiện kế hoạch- Theo dõi Đánh giá, đề xuất các phương án đảm bảo target traffic offline từng cửa hàng3. Xây dựng bộ quy chuẩn và quản lý POSM tại cửa hàng- Định hướng, lập kế hoạch, đưa ra ý tưởng, nội dung và quản lý việc trưng bày POSM tại cửa hàng.4. Tổ chức, triển khai các sự kiện bán hàng, khai trương- Quản ý, giám sát, lên kế hoạch khai trương cửa hàng mới- Phối hợp với bộ phận Mua Hàng - Kinh Doanh đề xuất các chương trình bán hàng để tăng doanh thu",
  "yeu_cau_cong_viec": "- Tốt nghiệp Đại học trở lên các chuyên ngành Marketing, Truyền thông và các chuyên ngành liên quan- Có ít nhất 2 năm kinh nghiệm ở vị trí Trưởng phòng Trade Marketing. Ưu tiên ứng viên có kinh nghiệm tại các chuỗi bán lẻ, đặc biệt ngành FMCG- Có kiến thức về các kênh Marketing Offline- Kỹ năng giao tiếp tốt- Có năng lực triển khai sâu sát- Tính tình vui vẻ, năng động, sáng tạo, nhiệt tình, trung thực, tận tâm trong công việc- Nhanh nhạy, linh hoạt, thích ứng nhanh với sự thay đổi",
  "quyen_loi": "- Tăng lương định kì hàng năm- Được hưởng đầy đủ chế độ bảo hiểm, thưởng lễ tết, nghỉ phép ,- Du lịch, teambuilding hàng năm- Thời gian làm việc: thứ 2 đến sáng thứ 7 hàng tuần, giờ hành chính",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/08/2022"
},
{
  "name": "Công ty Cổ phần Thương mại và Dịch vụ Trực tuyến OnePAY",
  "mo_ta_cong_viec": "To execute tests and do the test reports.To create/ update test Design specification basing on the requirementsTo perform bug reporting using an automated bug tracking systemProvide detailed report for Supervisor.Create plans, perform manual and automation tests for mobile applications, Website, Server.",
  "yeu_cau_cong_viec": "Having Knowledge to advice team and solving technical issue independently.Minimum of 1+ year proven testing experience.Ability to co-ordinate, communicate with customer, team on projects.Having experience with testing tool: Postman, JMeter (or same tool).",
  "quyen_loi": "- Competitive salary, 14 paid days annual leave.- Annual salary review & bonus twice a year.- Domestic & overseas technology workshops & conferences.- Others:• Comprehensive insurance• Annual teambuilding trips• Events for employees & their kids.• Full Insurance as Labor law,• Subvention for lunch, business trip ...",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/09/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN ICORP",
  "mo_ta_cong_viec": "- Gọi điện thoại cho các khách hàng mới, khách hàng tiềm năng và khách hàng hiện có để mời sử dụng dịch vụ của công ty và tư vấn, thương thảo, đàm phán, thuyết phục khách hàng sử dụng.- Tư vấn, hướng dẫn khách hàng hiểu và sử dụng các sản phẩm, dịch vụ của công ty. Giải đáp các thắc mắc và vấn đề cho khách hàng về dịch vụ của công ty.- Xây dựng mối quan hệ với khách hàng dựa trên sự tập trung vào nhu cầu mong muốn của khách hàng và chốt sales.- Phối hợp với các nhân viên kinh doanh và quản lý để đạt mục tiêu kinh doanh.- Báo cáo với cấp trên về tiến độ và kết quả kinh doanh- Tư vấn, hướng dẫn khách hàng hiểu và sử dụng các sản phẩm, dịch vụ của công ty.- Cụ thể sẽ trao đổi trong quá trình phỏng vấn.",
  "yeu_cau_cong_viec": "-  Ưu tiên có kinh nghiệm làm việc ở vị trí nhân viên Telesales/Sales/Chăm sóc khách hàng hoặc các vị trí tương đương- Có khả năng xử lí các tình huống bị từ chối hoặc các vấn đề phát sinh- Khả năng tư vấn thuyết phục, giao tiếp tốt.- Nghiêm túc, độc lập trong công việc.- Nhanh nhẹn, ham học hỏi, chủ động, trung thực và có tinh thần trách nhiệm cao.",
  "quyen_loi": "- Mức lương: Lương cứng 6tr + lương kinh doanh + phụ cấp- Phụ cấp ăn trưa.- Được hưởng các chế độ BHXH, BHYT, BHTN và các phúc lợi khác theo quy định của Luật lao động và của Công ty- Được đi du lịch và tham gia các hoạt động vui chơi, giải trí khác do công ty tổ chức hàng hàng năm.- Được đào tạo về chuyên môn khi làm việc.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 13/09/2022"
},
{
  "name": "Viettel Software Services",
  "mo_ta_cong_viec": "Xây dựng, tìm kiếm và phát triển nguồn ứng viên (Java, Python, Android, iOS, Business Analyst, Tester....) dựa trên kế hoạch tuyển dụngLiên hệ ứng viên, sắp xếp lịch phỏng vấn, sơ vấn ứng viênCập nhật, lưu trữ và quản lý thông tin ứng viênThực hiện công tác tuyển dụng theo quy trình của công tyTham gia xây dựng, triển khai, thực hiện các chương trình truyền thông, xây dựng thương hiệu tuyển dụng, và giữ nhân viên gắn bó lâu dài với công tyCác trách nhiệm khác theo yêu cầu của quản lý",
  "yeu_cau_cong_viec": "Có ít nhất 01 năm kinh nghiệm tuyển dụng (trong đó có ít nhất 06 tháng tuyển dụng trong lĩnh vực IT - vui lòng ghi rõ trong CV)Có kiến thức cơ bản về lĩnh vực CNTTMạng lưới tuyển dụng rộng, đa dạngKỹ năng đánh giá, giao tiếp, truyền đạt và ra quyết định tốtYêu thích công việc nhân sựThái độ nghiêm túc, ham học hỏi, sẵn sàng hoàn thành nhiệm vụ được giaoTư duy logic tốt, sáng tạo trong công việcBiết quản lý công việc và thời gian hiệu quả",
  "quyen_loi": "1. Chế độ lương, thưởng, thu nhập:Thu nhập cạnh tranh thỏa thuận theo kinh nghiệm và năng lựcNghỉ mát, thưởng ngày lễ và các ngày chỉ có ở Viettel như Ngày Sáng Tạo - 1/6, 22/12, quà Tết Dương, Tết Âm  tri ân Gia đình, người sinh thành. (Tổng package: 20-25 triệu/năm)Lương tháng 13 + Thưởng dự án + Thưởng KPITrợ cấp đi lại + Hỗ trợ ăn trưaReview, Xét tăng lương 2 lần/năm12 Ngày phép/năm + 3 ngày nghỉ dưỡng có lươngTham gia BHXH đầy đủ cùng gói bảo hiểm Pijico chăm sóc sức khỏe và tai nạn dành riêng cho Nhân viên Viettel2. Môi trường làm việcĐược làm việc trong Tập đoàn toàn cầu, tiên phong thực hiện sứ mệnh kiến tạo xã hội số.Môi trường mở, trẻ trung, năng động, trân trọng, yêu thương, tương hỗ & lắng nghe mỗi người từ những ý tưởng nhỏ nhất.Không gian làm việc xanh, mở, hiện đại.3. Cơ hội phát triển bản thânCó cơ hội thử sức trong lĩnh vực công nghệ tiên tiến, hiện đại nhất.Được thử sức với các dự án hấp dẫn, thử thách đủ lớn trong và ngoài nước để trưởng thành.Được trao quyền sáng tạo với đam mê của tuổi trẻ.Cơ hội học hỏi từ các chuyên gia hàng đầu, lãnh đạo và đồng nghiệp ưu tú.Cơ hội được đào tạo, trau dồi kĩ năng, chuyên môn để phát triển toàn diện.4. Địa điểm làm việcViettel Software Services : Tầng 5, Tòa nhà Thành Công, 80 Dịch Vọng Hậu, Cầu Giấy, Hà NộiThời gian làm việc: Từ thứ 2 đến thứ 6, nghỉ T7 & CN",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN ĐẦU TƯ YOPY VIỆT NAM",
  "mo_ta_cong_viec": "Xây dựng chiến lược chiến lược nội dung, chiến lược từ khoá giúp tăng thứ hạng website công ty trên các trang tìm kiếm chính.Đề xuất các thay đổi/cải thiện về cấu trúc website, content cũng như các yếu tố khác nhằm tối ưu hiệu quả SEOTheo dõi, đánh giá, giám sát các kết quả SEO.",
  "yeu_cau_cong_viec": "Nhiệt tình, trung thực, có tinh thần trách nhiệm với công việc.Có laptop cá nhânCó thể làm việc độc lập hoặc làm theo nhómCó khả năng nghiên cứu, tự triển khaiSử dụng thành thạo máy tính là một lợi thế",
  "quyen_loi": "Được đào tạo các kỹ năng về SEO, kỹ năng lập kế hoạch, thiết lập mục tiêu,...Thưởng dự án (trao đổi thêm khi phỏng vấn).Đánh giá và điều chỉnh tăng lương 6 tháng/lầnMôi trường làm việc trẻ trung, năng động, thân thiện.Cơ hội học hỏi, thăng tiến và phát triển sự nghiệp rộng mở.Bảo hiểm theo quy định của Nhà nước.Du lịch công ty, liên hoan.Gửi xe miễn phí, ăn trưa cùng công ty.Tận hưởng thời gian giải trí với máy PlayStation 4 5, bàn bi-a.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty cổ phần ứng dụng phần mềm mobio việt nam",
  "mo_ta_cong_viec": "Lập kế hoạch kiểm thử phần mềmViết tài liệu kịch bản kiểm thử phần mềmChuẩn bị data test.Thực hiện kiểm thử phần mềm trên, báo cáo lỗi của phần mềm lên các công cụ quản lý lỗi.Viết báo cáo kiểm thử phần mềm, thống kê phân loại lỗi của phần mềm.Thực hiện các công việc liên quan do trưởng nhóm phân công.",
  "yeu_cau_cong_viec": "Có từ 1 - 3 năm kinh nghiệm làm việcTốt nghiệp chuyên ngành như Công nghệ thông tin, Khoa học máy tính,....Đã từng học ít nhất 1 khoá tester là 1 lợi thế.Hiểu biết về test case, các công việc test cơ bản",
  "quyen_loi": "Mức lương:từ 9tr – 18tr, tuỳ kinh nghiệm và kỹ năng làm việc.Package lương:13 tháng lương cố định/năm, thưởng hiệu quả chung vào cuối năm (tuỳ tình hình kinh doanh hằng năm). Có cơ hội được đánh giá điều chỉnh thu nhập 1-2 lần/năm;Chế độ đãi ngộ cạnh tranh:- Chế độ thai sản đặc biệt cho nhân viên ( 20 triệu/1 CBNV sinh con);- Đóng bảo hiểm sức khoẻ hàng năm (Bảo hiểm VBI 4 – 8 triệu/CBNV/năm);- Chính sách đào tạo từ 10 – 15 triệu/CBNV/năm;- Chế độ thăm hỏi ốm đau, hiếu hỉ, du lịch, các ngày lễ, các hoạt động tri ân, chăm lo đời sống tinh thần nhân viên và thân nhân;- Đóng bảo hiểm y tế, bảo hiểm xã hội theo quy định của Nhà nước….;Môi trường làm việc:Chuyên nghiệp, thân thiện, cởi mở, tạo điều kiện phát triển cho CBNV; có cơ hội được làm việc cùng với những đồng nghiệp có nhiều năm kinh nghiệm trong lĩnh vực công nghệ.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "Công ty cổ phần ứng dụng phần mềm mobio việt nam",
  "mo_ta_cong_viec": "Tham gia phát triển các dự án về Web, Mobile của Công ty.Chuyên xây dựng các chức năng Front-end của Website, Web application, Mobile application;Tham gia tìm hiểu, đánh giá các công nghệ frontend để sử dụng trong dự án;Tham gia vào thiết kế và review source code;Báo cáo hàng ngày, hàng tuần cho cấp trên và team member trong dự án.",
  "yeu_cau_cong_viec": "Ứng viên đã có từ 1 - 3 năm kinh nghiệm làm Angular 2, Typescript trở lên.Có kiến thức sâu về: Angular (Angular 4 trở lên), HTML, CSS;Biết sử dụng LESS, SASS/Stylus.Có kinh nghiệm làm việc với Bootstrap, Foundation.Có kinh nghiệm trong việc làm responsive web.Sử dụng thành thạo các tool để phát triển dự án: SVN, GIT.Có thể làm việc thành thạo trên môi trường Linux (cài đặt, cấu hình, chạy các phần mềm trên server Linux).",
  "quyen_loi": "Mức lương: Từ 12 - 30 triệu/tháng (tuỳ kinh nghiệm và kỹ năng làm việc);Package lương: 13 tháng lương cố định/năm, thưởng hiệu quả chung vào cuối năm (tuỳ tình hình kinh doanh hằng năm). Có cơ hội được đánh giá điều chỉnh thu nhập 1-2 lần/năm;Chế độ đãi ngộ cạnh tranh:- Chế độ thai sản đặc biệt cho nhân viên ( 20 triệu/1 CBNV sinh con);- Đóng bảo hiểm sức khoẻ hàng năm (Bảo hiểm VBI 4 – 8 triệu/CBNV/năm);- Chính sách đào tạo từ 10 – 15 triệu/CBNV/năm;- Chế độ thăm hỏi ốm đau, hiếu hỉ, du lịch, các ngày lễ, các hoạt động tri ân, chăm lo đời sống tinh thần nhân viên và thân nhân;- Đóng bảo hiểm y tế, bảo hiểm xã hội theo quy định của Nhà nước….;Môi trường làm việc: Chuyên nghiệp, thân thiện, cởi mở, tạo điều kiện phát triển cho CBNV; có cơ hội được làm việc cùng với những đồng nghiệp có nhiều năm kinh nghiệm trong lĩnh vực công nghệ.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN CÔNG NGHỆ BLUE OCEAN",
  "mo_ta_cong_viec": "Giới thiệu các tính năng của phần mềm đến khách hàng.Cài đặt và triển khai hệ thống cho khách hàng theo yêu cầu của từng dự án.Hướng dẫn và đào tạo khách hàng sử dụng hệ thống phần mềm.Hỗ trợ khách hàng sử dụng phần mềm sau khi triển khai và tiếp nhận yêu cầu mới từ người dùng.Là chuyên gia trong việc quản lý các ứng dụng của MegaSchool, 789.Hỗ trợ bộ phận Kinh doanh trong công tác soạn thảo tài liệu kỹ thuật.Thực hiện các công việc khác khi có yêu cầu.",
  "yeu_cau_cong_viec": "Tốt nghiệp Đại học ngành Công nghệ thông tin, Khoa học Máy tính, Công nghệ phần mềm hoặc các ngành khác nhưng hiểu rõ về Tin học, máy tính là lợi thế.Có ít nhất 1 năm kinh nghiệm hỗ trợ khách hàng các dịch vụ kỹ thuật.Kỹ năng thuyết trình và giao tiếp tốt.Có kiến thức và kinh nghiệm về IT helpdesk là một lợi thế.Năng động và khả năng thích ứng cao cùng kỹ năng tổ chức và giải quyết vấn đề tốt.Có khả năng giao tiếp bằng tiếng Anh là một lợi thếĐam mê Giáo dục.",
  "quyen_loi": "Thu nhập cạnh tranh: từ 12-15tr/tháng tùy năng lực.Hình thức công việc: Toàn thời gian Từ thứ 2 đến thứ 6(Sáng: 8h-12h, Chiều: 13h00-17h00.)Được tham gia đầy đủ BHXH, BHYT, BHTN,…theo quy định luật lao động.Lộ trình thăng tiến, có cơ hội lên vị trí cao hơn xét theo kết quả làm việc.Thưởng các ngày sinh nhật, lễ, Tết…Làm việc trong ngành giáo dục, có cơ hội và môi trường sử dụng và phát triển tiếng Anh.Được cập nhật và sử dụng các công nghệ mới nhất.Được đào tạo, hướng dẫn các kỹ năng nghiệp vụ (On-job training).Các hoạt động xây dựng đội nhóm, du lịch công ty.Lương tháng 13, thưởng cuối năm theo kết quả kinh doanh của công tyKhông bắt buộc đồng phục, thoải mái, linh động trong lựa chọn trang phục.Phụ cấp laptop, gửi xe.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "Công ty TNHH Dịch vụ - Giải pháp - Công nghệ Ong Vàng (Beetech Solutions)",
  "mo_ta_cong_viec": "- Phát triển các chức năng nâng cao trong hệ thống (AddOns), thiết kế biểu mẫu, báo cáo theo yêu cầu dự án- Lập trình các ứng dụng tích hợp SAP Business One với hệ thống khác.- Cài đặt, cấu hình hệ thống.- Thiết kế, xây dựng các tài liệu kỹ thuật liên quan đến dự án.- Làm việc cùng với đội tư vấn triển khai phân tích và giải quyết các vấn đề trong việc sử dụng phần mềm, phát triển phần mềm theo yêu cầu của mỗi dự án dưới sự kiểm soát của Leader và Project manager.- Kiểm tra và khắc phục sự cố về việc sử dụng phần mềm.- Hỗ trợ người dùng các vấn đề liên quan đến kỹ thuật.",
  "yeu_cau_cong_viec": "- Tốt nghiệp đại học, cao đẳng trở lên các chuyên ngành liên quan đến lập trình.- Sử dụng tốt MS Office.- Sử dụng tốt một trong các ngôn ngữ C#, .NET, JSON, XML,...- Làm việc được trên các nền tảng CSDL như SQL, HANA- Có khả năng đọc hiểu tài liệu tiếng anh- Khả năng nắm bắt công nghệ mới nhanh chóng sau khi qua các khóa đào tạo.- Chủ động làm việc độc lập, khả năng phối hợp theo nhóm.- Có khả năng phân tích, phân loại, xắp xếp thứ tự ưu tiên các yêu cầu về mặt kỹ thuật, quản trị thời gian phù hợp để hoàn thành mục tiêu chung của dự án.- Sẵn sàng đi công tác theo dự án.- Có kinh nghiệm phát triển hệ thống SAP Business One là một lợi thế.- Ứng viên có từ 0-2 năm kinh nghiệm, đặc biệt các bạn mới ra trường sẽ được đào tạo.",
  "quyen_loi": "- Lương thỏa thuận theo năng lực, ứng viên chưa có kinh nghiệm sẽ được đào tạo.- Được tham gia BHXH, BHYT, BHTN đầy đủ.- Được đào tạo, hướng dẫn thêm về chuyên môn từ các chuyên gia trong ngành.- Môi trường làm việc thân thiện, năng động.- Thưởng tết, lương tháng 13.- Du lịch hàng năm.- Review lương hàng năm theo năng lực.- Được huấn luyện, đào tạo sản phẩm và quy trình phát triển hệ thống theo chuẩn quốc tế tại nội bộ công ty hoặc trực tiếp từ hãng SAP trong và ngoài nước.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty TNHH Dịch vụ - Giải pháp - Công nghệ Ong Vàng (Beetech Solutions)",
  "mo_ta_cong_viec": "- Triển khai, cài đặt hệ thống phần mềm hệ thống quản trị doanh nghiệp SAP B1;- Xây dựng tài liệu hướng dẫn và hỗ trợ sử dụng phần mềm;- Tiếp nhận và phân tích yêu cầu từ khách hàng để tư vấn - hướng dẫn và xử lý; xây dựng tài liệu giải pháp- Kết hợp với phòng Lập trình để cập nhật, bổ sung và phát triển các chức năng, tính năng chương trình theo yêu cầu của khách hàng;- Xây dựng liệu kiểm thử và Kiểm tra phần mềm, đảm bảo chất lượng hệ thống trước khi triển khai và bàn giao cho khách hàng- Thực hiện kiểm thử, đánh giá mức độ phù hợp của phần mềm đối với các yêu cầu của người dùng.- Thực hiện các yêu cầu công việc khác theo phân công, chỉ định của cấp trên.",
  "yeu_cau_cong_viec": "- Tốt nghiệp Cao đẳng/Đại học chuyên ngành Hệ thống thông tin, CNTT, Tin học Kế toán, Quản trị kinh doanh, Kế toán, Kinh tế.- Sử dụng tốt MS Office- Ưu tiên có kinh nghiệm tư vấn và triển khai các phần mềm ERP hoặc phần mềm kế toán có liên quan (SAP, Oracle, Bravo, Fast, Misa…).- Có kiến thức nền tảng về tài chính kế toán là một lợi thế. Với sinh viên mới ra trường sẽ được đào tạo.- Biết SQL và các ngôn ngữ lập trình là một lợi thế.- Đọc hiểu tiếng Anh tốt.- Chấp nhận công tác xa theo yêu cầu triển khai dự án.- Có khả năng làm việc với cường độ cao, chịu áp lực công việc tốt.- Có khả năng làm việc độc lập, chủ động cũng như làm việc nhóm tốt.- Có khả năng tổ chức công việc, viết tài liệu, trình bày, thuyết trình tốt- Tinh thần cầu tiến, đam mê và không ngừng học hỏi.- yeu_cau_cong_viec kinh nghiệm từ 2 năm trở xuống",
  "quyen_loi": "- Lương từ 8-15tr (thỏa thuận theo năng lực) + thưởng KPI + thưởng nóng...., ứng viên chưa có kinh nghiệm sẽ được đào tạo.- Được tham gia BHXH, BHYT, BHTN đầy đủ.- Được đào tạo, hướng dẫn thêm về chuyên môn từ các chuyên gia trong ngành.- Môi trường làm việc thân thiện, năng động.- Thưởng tết, lương tháng 13.- Du lịch hàng năm.- Review lương hàng năm theo năng lực.- Được huấn luyện, đào tạo sản phẩm và quy trình phát triển hệ thống theo chuẩn quốc tế tại nội bộ công ty hoặc trực tiếp từ hãng SAP trong và ngoài nước.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "Công ty TNHH Tiến Bộ Sài Gòn",
  "mo_ta_cong_viec": "•\tThiết kế UI/UX cho App, Website, Systerm và các sản phẩm khác theo tiêu chí thân thiện với người dùng.•\tPhối hợp chặt chẽ với các bộ phận liên quan (Customer, Marketing, Development, QA,…) để lựa chọn phương án thiết kế UX xuyên suốt dự án sản phẩm/dịch vụ•\tNghiên cứu và cập nhật các xu hướng thiết kế UI/UX hiện nay•\tĐảm nghiệm các công việc khác theo sự phân công của cấp trên",
  "yeu_cau_cong_viec": "•\tTốt nghiệp cao đẳng trở lên, chuyên ngành thiết kế•\tCó ít nhất 2 năm kinh nghiệm ở vị trí tương đương•\tCó khiếu thẩm mỹ khá, nhận diện và biết sắp xếp bố cục hợp lý.•\tCó kinh nghiệm đánh giá thông qua Portfolio về UI/UX•\tCó kiến thức về HTML/CSS là một lợi thế.",
  "quyen_loi": "Môi trường làm việc trẻ trung, thân thiện.Được tạo thuận lợi về cơ sở vật chất, trang thiết bị phục vụ cho công việc.Đồng nghiệp vui vẻ, nhiệt tình và luôn luôn hỗ trợ mọi lúc mọi nơi.Hưởng đầy đủ các chế độ BHXH, BHYT, BHTN theo quy định của nhà nước hiện hành.Tháng lương thứ 13, thưởng hoàn thành đúng tiến độ dự án…Xét tăng lương 1 năm 1 lần.Du lịch hè.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công ty TNHH Tiến Bộ Sài Gòn",
  "mo_ta_cong_viec": "Tiếp nhận các yêu cầu từ khách hàng, phân tích quy trình nghiệp vụ, đề xuất các phương án khả thi.Thực hiện phân tích và xây dựng tài liệu đặc tả yêu cầu nghiệp vụ, tài liệu thiết kế các trường hợp sử dụng (usecase), giao diện mẫu (prototype, wireframe) và các quy trình nghiệp vụ (workflow) cho đội phát triển phần mềm.Phân tích các rủi ro liên quan đến các sản phẩm phần mềm, cơ sở dữ liệu và đề xuất các giải pháp khắc phục (nếu có); đóng góp các ý kiến, sáng kiến cải tiến sản phẩm phần mềm, giải pháp công nghệ.Hỗ trợ đội ngũ kiểm tra chất lượng sản phẩm phần mềm xây dựng kịch bản kiểm chứng đảm bảo testcase đầy đủ và đáp ứng đúng đặc tả nghiệp vụ.Thực hiện kiểm duyệt chất lượng sản phẩm đảm bảo đáp ứng đúng yêu cầu nghiệp vụ.Hỗ trợ các vị trí khác trong quá trình triển khai dự án.Nghiên cứu, phân tích, so sánh và đề xuất giải pháp phù hợp để áp dụng, triển khai các dự án phần mềm đáp ứng nhu cầu hiện tại và tương lai.Thực hiện các công việc khác theo yêu cầu của bộ phận quản lý hoặc Ban Giám đốc.",
  "yeu_cau_cong_viec": "1.\tYêu cầu chuyên môn:Tốt nghiệp Đại học, Cao đẳng hoặc tương đương chuyên ngành Công nghệ thông tin, Công nghệ phần mềm, Khoa học máy tính.Có ít nhất 3 năm kinh nghiệm làm việc ở vị trí tương tự.2.\tYêu cầu kỹ năng:Có khả năng xây dựng và thiết kế tài liệu đặc tả yêu cầu nghiệp vụ, xây dựng kịch bản kiểm thử (UAT)Sử dụng tốt các công cụ hỗ trợ phân tích thiết kế.Có kiến thức tốt về CNTT và hiểu được thiết kế kỹ thuật.Có kỹ năng về UI/UX Designer là 1 lợi thế.Có khả năng làm việc theo nhóm, có trách nhiệm cao, óc sáng tạo và chăm chỉ.Nhanh nhẹn, cẩn thận, tỉ mỉ, chịu được áp lực công việcNăng động, cầu tiến, sáng tạo, chủ động trong công việc.Biết và sử dụng được GIT là một lợi thế",
  "quyen_loi": "1.\tquyen_loi chungMôi trường làm việc trẻ trung, thân thiện.Được tạo thuận lợi về cơ sở vật chất, trang thiết bị phục vụ cho công việc.Đồng nghiệp vui vẻ, nhiệt tình và luôn luôn hỗ trợ mọi lúc mọi nơi.Hưởng đầy đủ các chế độ BHXH, BHYT, BHTN theo quy định của nhà nước hiện hành.Tháng lương thứ 13, thưởng hoàn thành đúng tiến độ dự án…Xét tăng lương 1 năm 1 lần.Du lịch hè.2.\tMức lươngTối thiểu 800$.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công ty TNHH Tiến Bộ Sài Gòn",
  "mo_ta_cong_viec": "– Lập trình website, web application.– Xây dựng front-end (UI/UX), back-end cho ứng dụng trên nền tảng web.- Xây dựng các hàm API tích hợp các hệ thống hoặc với đối tác.– Tham gia vào quá trình phân tích, thiết kế, nâng cấp và phát triển hệ thống.- Góp ý cho designer chỉnh sửa lại giao diện để đảm bảo các tính năng logic– Tham gia nghiên cứu, tìm hiểu/cập nhật và đề xuất các vấn đề liên quan đến việc duy trì/xây dựng/phát triển phần mềm.– Tham gia xây dựng tài liệu phát triển, nâng cấp, tối ưu, sửa lỗi …- Tham gia với đội ngũ kỹ thuật để giải quyết các vấn đề kỹ thuật chung, phức tạp.- Thực hiện các công việc khác theo yêu cầu của bộ phận quản lý hoặc Ban Giám đốc.",
  "yeu_cau_cong_viec": "-\tTốt nghiệp Đại học, Cao đẳng hoặc tương đương chuyên ngành Công nghệ thông tin, Công nghệ phần mềm, Khoa học máy tính.-\tThành thạo các kỹ thuật cơ bản trong công nghệ .NET: C#, MSSQL Server, ADO.NET, MVC / MVC5, WebService, XML…-\tHiểu biết một số công nghệ sử dụng cho website: HTML / HTML5, CSS / CSS3, Javascript, Ajax, jQuery, Angularjs…-\tBiết sử dụng LINQ, Entity Framework, KendoUI là một lợi thế.-\tHiểu biết lập trình mobile là một lợi thế-\tNhanh nhẹn, cẩn thận, tỉ mỉ, chịu được áp lực công việc.-\tNăng động, cầu tiến, sáng tạo, chủ động trong công việc.",
  "quyen_loi": "-\tMức lương theo thỏa thuận.-\tMôi trường làm việc trẻ trung, năng động, hoạt động văn hóa phong phú, điều kiện làm việc hiện đại, văn minh;-\tXét duyệt thăng cấp và lương, thưởng hàng năm-\tĐược tham gia các khóa Đào tạo nâng cao chuyên môn và kỹ năng do Công ty tổ chức;-\tCơ hội để phát triển nghề nghiệp với công ty;-\tHưởng đầy đủ các chế độ BHXH, BHYT, BHTN theo quy định của nhà nước hiện hành.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH SAMSUNG SDS VIỆT NAM",
  "mo_ta_cong_viec": "Identify and define system security requirementsSecure Coding and Information Security GuideDesign security architectureApplication penetration Testing (Web/Android/iOS/Window program etc.)Check the security weakness of source code developed in various languagesOpen source security verificationInfra structure/Cloud Security VerificationReport security issues",
  "yeu_cau_cong_viec": "Experience of web/mobile application penetration testingExperience with web related technologies and network protocolsExperience of security test toolTechnical knowledge of operating system and databaseBasic coding skills, such as Java, HTML and other languagesCertifications such as OSCP,OSWE, CEH desiredExperience of Bug Bounty or CTF awardProblem solving skills and communication skills",
  "quyen_loi": "SALARY, INSURANCE• Salary negotiable• 100% salary during 2-month probation• Full-salary insurance starting right from probation period• 3 times bonus per year• Health check once per year• Accident insuranceTRAINING & DEVELOPMENT:• 1000$ for each employee per year for personal training• Oversea training opportunitiesOTHER BENEFITS:• Numerous internal activities: team bonding, team training,…• Gifts for each employee on 30/4,1/5; 2/9....(in cash)• Bonus for employee having Toeic or Topik certificates.• 5 working days per week to ensure work-life balance",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công Ty TNHH Công Nghệ Hữu Trí",
  "mo_ta_cong_viec": "mo_ta_cong_viecTriển khai nội dung bài viết trên hệ thống Website của công ty. Các dạng bài viết tin tức.Chỉnh sửa, cập nhật nội dung thông tin mới trên các bài viết. Thực hiện các công việc khác liên quan theo hướng dẫn.Thời gian làm việc cực kỳ linh hoạt. Các bạn nhân viên tự lên kế hoạch, sắp xếp công việc theo tuần. Công ty chỉ quan tâm đến việc thực hiện đúng KPI cam kết và chất lượng công việc. Làm việc cả online hoặc offline.",
  "yeu_cau_cong_viec": "Có khả năng làm việc độc lập và đảm bảo tiến độ KPI đã cam kết.Các bạn mới sẽ được đào tạo theo chương trình chuẩn riêng của cty.Chăm chỉ, tích cực, nghiêm túc, đảm bảo tiến độ và hoàn thành KPI.Có kỹ năng viết hoặc thích viết. Có định hướng lâu dài.",
  "quyen_loi": "- Được đào tạo chuyên sâu về kỹ năng content.- Được hướng dẫn đào tạo phát triển thêm các kỹ năng khác.- Được thưởng tháng lương thứ 13, thưởng các ngày lễ tết.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH CÔNG NGHỆ RIKAI",
  "mo_ta_cong_viec": "Phát triển các trang Web, API trên nền tảng .Net Core/.Net FrameworkXây dựng tài liệu Design (HLD, LLD).",
  "yeu_cau_cong_viec": "1. Kinh nghiệm bắt buộcCó ít nhất 1 năm kinh nghiệm làm việc với .NET Core.Sử dụng thành thạo ngôn ngữ lập trình C#.Có kinh nghiệm lập trình SQL/NoSQL databases.Thành thạo sử dụng version control system Git (Github, Gitlab…).Có khả năng nghiên cứu công nghệ, Framework mới.2. Những kỹ năng ưu tiênCó thêm kinh nghiệm sử dụng .Net Framework.Có hiểu biết về 1 trong các dịch vụ Cloud (AWS, GCP, Azure…).Có kinh nghiệm làm việc với các ứng dụng kiến trúc, thiết kế mô hình, thiết kế DatabaseƯu tiên các ứng viên có khả năng sử dụng tốt Tiếng Anh chuyên ngành và giao tiếp cơ bản.",
  "quyen_loi": "Mức lương thưởng cạnh tranh, hấp dẫn theo năng lực, trao đổi chi tiết trong buổi phỏng vấn;Chính sách premium insurance siêu xịn sò dành riêng cho Rikai-er;Thời gian làm việc linh động (flexible time)Có cơ hội đi onsite nước ngoài, tuỳ thuộc dự ánNhiều chương trình đào tạo hard/soft skills chất lượng và miễn phí trong công ty;Happy hour, CLB bóng đá, sinh nhật, trung thu, quốc tế thiếu nhi,… siêu thú vị;Mỗi năm sẽ được đi du lịch xa 01 lần, có quỹ team building, company trip cho mỗi team;Môi trường làm việc năng động, chuyên nghiệp, teammate nhiệt tình;Công ty định hướng mở rộng quy mô lớn, cơ hội thăng tiến và phát triển bản thân cao.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN RIKAI MIND",
  "mo_ta_cong_viec": "- Thông dịch trong các cuộc họp với khách hàng.- Hỗ trợ PM dự án xử lý các vấn đề phát sinh trong việc communicate với khách hàng.- Tiếp nhận và quản lý tài liệu, yêu cầu từ Khách hàng Nhật, từ đội dự án.- Dịch các email, tài liệu trao đổi giữa đội dự án và Khách hàng Nhật .- Truyền tải và giải thích văn hoá, phong cách Nhật cho team dự án- Review lại tài liệu của các thành viên.",
  "yeu_cau_cong_viec": "- Tiếng Nhật từ N2- Là phiên dịch/biên dịch viên chuyên nghiệp- Khả năng học hỏi, làm việc độc lập cao; có tinh thần trách nhiệm, làm việc nhóm tốt.- Ưu tiên các bạn có kinh nghiệm làm việc trong các công ty về CNTT- Ứng viên có kinh nghiệm học tập, làm việc tại Nhật là một lợi thế",
  "quyen_loi": "- Mức lương thưởng cạnh tranh, hấp dẫn theo năng lực, trao đổi chi tiết trong buổi phỏng vấn;- Chính sách premium insurance siêu xịn sò dành riêng cho Rikai-er;- Thời gian làm việc linh động (flexible time)- Có cơ hội đi onsite nước ngoài, tuỳ thuộc dự án- Nhiều chương trình đào tạo hard/soft skills chất lượng và miễn phí trong công ty;- Happy hour, CLB bóng đá, sinh nhật, trung thu, quốc tế thiếu nhi,... siêu thú vị;- Mỗi năm sẽ được đi du lịch xa 01 lần, có quỹ team building, company trip cho mỗi team;- Môi trường làm việc năng động, chuyên nghiệp, teammate nhiệt tình;- Công ty định hướng mở rộng quy mô lớn, cơ hội thăng tiến và phát triển bản thân cao.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "Công ty CP Công nghệ phần mềm và nội dung số OSP",
  "mo_ta_cong_viec": "- Hỗ trợ tạo nguồn ứng viên;- Đăng tin tuyển dụng trên các kênh tuyển dụng của Công ty;- Theo dõi và tổng hợp hồ sơ tuyển dụng hàng ngày;- Liên hệ ứng viên, setup quá trình phỏng vấn;- Tham gia hỗ trợ event tuyển dụng;- Một số nhiệm vụ khác theo yêu cầu của quản lý.",
  "yeu_cau_cong_viec": "- Các bạn sinh viên năm 4 mong muốn theo đuổi lĩnh vực Nhân sự;- Ưu tiên ứng viên có thể tham gia thực tập Fulltime;- Ưu tiên ứng viên có khả năng xây dựng content, thiết kế hình ảnh ở mức cơ bản;- Nhiệt tình, chủ động, ham học hỏi;- Có khả năng sử dụng cơ bản MS Office.",
  "quyen_loi": "- Mức hỗ trợ: 1.000.000 - 3.000.000 VND / tháng + thưởng;- Cơ hội học hỏi kinh nghiệm về tuyển dụng, xây dựng thương hiệu nhà tuyển dụng;- Cơ hội trở thành nhân viên chính thức sau quá trình thực tập;- Hỗ trợ dấu trong quá trình thực tập;- Cơ hội làm việc tại doanh nghiệp Top 10 CNTT uy tín nhất Việt Nam;- Nghỉ Thứ Bảy, Chủ Nhật và các ngày lễ theo quy định.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/08/2022"
},
{
  "name": "CÔNG TY TNHH MEDIASTEP SOFTWARE VIỆT NAM",
  "mo_ta_cong_viec": "We are looking for DevOps to join our team to continue to enhance our platform and build new features with the latest technology.You will be working on the newest O2O e-commerce platform in Vietnam and beyond.International environment. English and Vietnamese spoken.You will be working with a super high performance team delivering software that people use everyday.Job Description:- Manage VM/Cloud infrastructure ( Citrix Hypervisor and AWS )- Develop and maintain scripts and tools currently using Python /Bash- Building, contributing to our monitoring system.- Prepare CI/CD.- Perform designing, optimizing infrastructure to make our system more stable.- Skills and experience:- Learning agility: willing to learn and learn fast- A team player who can also work independently with minimal supervision- Computer science degree / equivalent degree / hand-on experience- AWS, AZURE Infrastructure Manage and Cost Optimization",
  "yeu_cau_cong_viec": "- 2 year of experience or more- Infrastructure as code : Terraform .- Good understanding of TCP/IP, UDP, HTTP, SSL/TLS and DNS- Experience with system administration or infrastructure maintenance- Good knowledge of design patterns, system architecture, and best practices- Practical cloud experience with AWS,Azure or GCP.- Practical experience with Docker containerization.- Bash, Python Scripting.- Continuous Integration and Continuous Deployment (CI/CD): Jenkins, GitlabCI;-  Nice to have :AWS SysOps / Solution Architect certification.Agile development processes experience is a plus. English: speaking, writing",
  "quyen_loi": "- Salary: negotiable- 13+14 month performance based bonus- 15 days annual leave- Working with the latest technology- Agile/scrum environment",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 18/07/2022"
},
{
  "name": "Công ty CP Công nghệ phần mềm và nội dung số OSP",
  "mo_ta_cong_viec": "Tham gia phát triển dự án mobile theo phân công của công tyLàm việc theo mô hình phát triển dự án Agile, ScrumCùng cấp quản lý phân tích và thiết kế các tính năng sản phẩm.Nghiên cứu công nghệ mới, đưa ra giải pháp áp dụng vào sản phẩm dịch vụ của công ty.Thực hiện bảo trì và nâng cấp các sản phẩm dịch vụ của công ty.Phối hợp với đồng nghiệp trong nhóm để hoàn thành nhiệm vụ.Thực hiện các công việc khác theo phân công của cấp quản lý.",
  "yeu_cau_cong_viec": "Tốt nghiệp từ đại học trở lên các chuyên ngành về CNTTKinh nghiệm 2-4 năm lập trình ứng dụng mobile đa nền tảng (iOS và Android), trong đó ít nhất 2 năm sử dụng React NativeƯu tiên ứng viên có ứng dụng trên Apple App Store, Android Play Store với trên 1000 người dùngKiến thức tốt về OOP, MVVM, cấu trúc dữ liệu và giải thuậtKỹ năng lập trình TypeScript tốt. Có kinh nghiệm code với Objective-C / Switf, Android / Java là một lợi thếCó kiến thức về SQL, MySQLCó kinh nghiệm code với Objective-C / Swift, Android / Java, có thể xây dựng native moduleTích hợp thư viện bên thứ 3Thành thạo công cụ phát triển, debugNắm bắt được quy trình phát triển phần mềm",
  "quyen_loi": "Mức lương thỏa thuận phù hợp với năng lực ứng viênThưởng tháng lương thứ 13 + hiệu quả làm việc vào cuối năm tài chính.Thưởng dịp tết (tết dương và tết âm), dịp lễ (30/04-1/5; 2/9; …) sinh nhật,hiếu-hỷ…Review đánh giá tăng lương hàng nămNghỉ phép 12 ngày/năm, nghỉ ốm/nghỉ chế độ thai sản/hiếu hỉ… theo luật lao độngLàm việc tại công ty quy mô lớn, quy trình làm việc chuyên nghiệp, được khuyến khích sáng tạo và phát triển các ý tưởng mớiMôi trường trẻ, năng động, chuyên nghiệp, sếp trẻ tâm lý, đồng nghiệp thân thiện, văn hóa trao đổi thẳng thắn, cởi mở trên tinh thần hỗ trợ cùng phát triểnHọc hỏi kinh nghiệm trực tiếp từ các Chuyên gia hàng đầu.Được tài trợ 100% hoặc tham gia các khóa đào tạo kỹ năng, chuyên môn hàng năm, thi lấy chứng chỉ để phục vụ cho công việc.Được hưởng đầy đủ các chế độ BHYT, BHXH,BHTN.Du lịch hàng năm, teambuilding, event...",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH INTELLIGENT T&E",
  "mo_ta_cong_viec": "As a member of QC team, you will be in charge of QA/QC in mobile apps (native, android/iOS) and web apps (Front-end, API):Understand requirements, build test casesWork closely with the development team to clarify technical designs.Participate in research and propose improvement processes, test products.Perform the test with multiple technical testing corresponding to test plan or request from superiorCheck and manage the application quality of products in Japanese.",
  "yeu_cau_cong_viec": "Background in IT or at least 6 months of experience in manual testing.Knowledge of using tracking bugs and task management tools.Mastering the testing process and techniques.Self-motivated, proactive, eager to learn new technologiesTeamwork, Communication, and interpersonal skills.Basic English (reading, writing)BIG PLUS IF YOU HAVE THESE:Experience coding/ using QA software tools and processes is an advantage.Experience in projects related to the Japanese market is preferred.Knowing Japanese is a plus",
  "quyen_loi": "Great salary package. Year-end Bonus.Salary and performance review TWICE a year.MacBook is provided.A young, friendly work environment with highly-skilled team membersTraining and coaching program from our expert developers.Annual health check-ups for all staff.Self-serving coffee machine, drinks, and a pantry full of sweets and snacks.Monthly party with food and drinks.Team Building, Company Trip,... and other big events.Free language training: English and Japanese.Opportunity to go work on-site in Japan.Gifts or allowances for wedding, maternity, Women’s day, and Children DaySports clubs to maintain your balanced health: running, football, badminton",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 14/08/2022"
},
{
  "name": "CÔNG TY TNHH SAMSUNG SDS VIỆT NAM",
  "mo_ta_cong_viec": "* Solution project:Planning, define, consulting QA activites related to projectLeading eisp meeting to confirm scope, QA areas & schedule of Product Validation (PV) for projectGuide/training quality process for dev teamDiscuss/communication with HQ PM, GDCV PM, QA members about project & testing progress, issue ariseIssue tracking & report (Jira Confirm, Dev. Progress check)Perform inspection (Each QA area progress check, Entry Criteria check to meet target before start PV.. )Perform Code inspection (Code review, SAM, Repository check, Code Inspection)Make PV Report & share to related departments* Operation project:1. Performing Operation level audit to check the operation level of GDCV project such as: operation environment, service availability, service request/change management, failure management, etc., in the first and second half of the year :Selection of inspection/audit project targetDiscussing/Review with operation department about the target & make planAudit documents, data, interview PM/operatorDiscussing with operation department about audit result : Strength points & improvement requirement pointsMake report & share with related departmentsFollowing /Guide PM about the improvement requirement items after finish the audit (corrective action result)2. Perform operation transfer inspection when have any request3. Monitor operation project transfer status & analysis, report issues when have any",
  "yeu_cau_cong_viec": "4 - 5 Years (at least 3 years for experience in quality management related fields : Tester, PQA, QC)Quality inspection, auditing, quality management and testing experience, Process Quality AssuaranceExperience with implementation of corrective action programsStrong computer skills including Microsoft Office, QA applications (Jira, Confluence, SonarQue…) and databasesKnowledge of tools and methodologies of QACertifications including Quality Auditor, Quality Engineer, Quality Improvement Associate (ISO, ITIL, ISTQB..) is an advantage",
  "quyen_loi": "SALARY, INSURANCE• Salary negotiable• 100% salary during 2-month probation• Full-salary insurance starting right from probation period• 3 times bonus per year• Health check once per year• Accident insuranceTRAINING & DEVELOPMENT:• 1000$ for each employee per year for personal training• Oversea training opportunitiesOTHER BENEFITS:• Numerous internal activities: team bonding, team training,…• Gifts for each employee on 30/4,1/5; 2/9....(in cash)• Bonus for employee having Toeic or Topik certificates.• 5 working days per week to ensure work-life balance",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "FPT Smart Cloud (FCI)",
  "mo_ta_cong_viec": "Customized to specific need: Providing cloud-based products and solutions customized to each industry;All-in-one Platform: Consolidating FPT Smart Cloud technology and diverse business solutions all in one platform;Local market leadership: Outstanding Cloud and AI technology infrastructure and platform to help local businesses grow their products and services online;Deliver the future: Help customers achieve business outcomes faster by integrating world-class processes and technology.Main responsibilities:In charge of product MKT campaign implementation & support for both 2 product platforms FPT Cloud and FPT AI, including but not limited to client workshops, industry events, PR campaign, digital campaign;Support in the development of sales materials for business development team;In charge of corporate communication activities in HCMC office, including internal communication, corporate branding activities;Support channel marketing activities, work closely with channel management team to develop activities to engage major partners;Other tasks as assigned by managers.",
  "yeu_cau_cong_viec": "Bachelor's degree in Marketing or related fields;2-3 years of experience in product marketing, event management, general communication;Excellent communication skill & people skill;Quick – thinking, strong problem-solving skill;Able to work independently;Fluency in English;Proficient in using Microsoft Office, Excel;Experience and knowledge of software/IT is an advantage.",
  "quyen_loi": "Salary: up to 330 million/year;Full benefits according to current labor law;Welfare policies according to the Company's regulations are diverse: Annual health check; Vacation, Course sponsored;FPT health care for employees (Financial support with medical examination and treatment costs at all hospitals);Gratitude activities, taking care of employees’ mental health;Friendly, open, respectful working environment;Vacation: participate in large-scale cultural activities of the company and corporation as a whole;Details to be discussed during the interview.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH ĐẦU TƯ VÀ PHÁT TRIỂN SÀI GÒN LAND",
  "mo_ta_cong_viec": "- KIỂM TRA, SỮA CHỮA HỖ TRỢ THIẾT BỊ VĂN PHÒNG- QUẢN LÝ WEBSITE CÔNG TY - FANPAGE CÔNG TY-  LẬP TRÌNH WEBSITE, SỬA LỖI WEBSITE-  PHOTOSHOP, AI THIẾT KẾ BANNER TUYỂN DỤNG - BANNER DỰ ÁN- SỬ DỤNG CÁC CÔNG CỤ SEO WEBSITE NHƯ: GOOGLE ANYLYTICS, GOOGLE SEARCH CONSOLE....",
  "yeu_cau_cong_viec": "Kinh nghiệm từ 1 đến 3 nămThành thạo các kỹ năng về quản lý, sửa lỗi và lập trình webNhanh nhẹn, chịu khó",
  "quyen_loi": "Thưởng lễ, tết, du lịch hàng nămTham gia các hoạt động hộ thao hàng nămLàm việc trong môi trường năng động, cơ hội thăng tiếnCác chế độ khác theo quy định của công ty",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty Cổ phần Tin học - Viễn thông Hàng không",
  "mo_ta_cong_viec": "Quản trị, vận hành, đảm bảo hoạt đông các hệ thống trên môi trường nhiều loại OS (Win/Linux/Unix), CSDL( Oracle, MS SQL, Postgrep, MySQL ..), Oracle Portal/Weblogic/.Net/Rhel JBOSS .Quản trị hệ thống server application, database và hệ thống lưu trữ Storage, SAN…Xây dựng, thiết kế và tham gia triển khai các giải pháp ứng dụng trên các môi rường hệ điều hành, phần mềm ứng, cơ sở dữ liệu khác nhau và đa dạng.",
  "yeu_cau_cong_viec": "Có kinh nghiệm làm việc: 3 năm trở lên.Đã tham gia hoặc chủ trì : Thiết kế/triển khai hoặc quản trị các hệ thống liên quan đến HĐH, CSLDL cho các doanh nghiệp có 50 user trở lên.Ưu tiên ứng viên có ngoại ngữ (Tiếng Anh) tốtTốt nghiệp Đại học/Cao đẳng/Trung cấp chuyên ngành CNTT, Điện tử hoặc Viễn thôngCó một hoặc các chứng chỉ nghề về HĐH (Win server/Linux/Unix/RHEL), CSDL (Oracle, SQL Server), Ảo hóa (VMware, VM Unix, Cloud)Có kinh nghiệm cài đặt, sửa chữa các lỗi của server và/hoặc HĐH(OS), CSDL.Có hiểu biết về các loại phần cứng và phần mềm, sử dụng để thiết lập và tích hợp một hệ thống ứng dụng.Có hiểu biết về việc thiết lập, khai thác các quy định tiêu chuẩn về anh ninh và bảo mật trên HĐH(OS), CSDL, các phần mềm ứng dụng cài đặt trên serverCó hiểu biết về môi trường mạng, an ninh thông tinCó khả năng tiếp thu nhanh các công nghệ mới và khả năng xử lý sự cố - Có kỹ năng làm việc nhóm, giao tiếp với người sử dụng hệ thống/dịch vụ",
  "quyen_loi": "Mức lương hấp dẫn, cạnh tranh, upto $2000Nhân viên có năng lực tốt có thể ký hợp đồng chính thức khi chưa hết thời gian thử việcMôi trường làm việc năng động, thân thiện, cơ hội thăng tiến.Tăng lương theo hiệu quả công việc và cam kết đầy đủ các chế độ dành cho người lao động theo như quy định pháp luật hiện hành.Tất cả người lao động ký HĐLĐ với công ty đều được đóng và hưởng chế độ BHXH, BHYT, BHTN theo đúng quy định của Pháp luật.Được khám sức khỏe định kỳ hàng năm.Được cấp tiền trang phục hàng năm.Được hưởng chế độ nghỉ mát hàng năm.Được hỗ trợ các loại phụ cấp tùy thuộc vào đặc thù của Công việcĐược hưởng Phụ cấp ăn trưa.Được mua vé giảm theo chế độ của Tổng công ty HKVN (Vietnamairlines) và Hãng Hàng không Jestar pacific (JPA).Lao động nữ được được hưởng các chế độ theo đúng quy định của Phát luật nhà nước và Công ty.Bảo hiểm con người;Bảo hiểm tai nạn lao độngTùy theo điều kiện hoạt động SXKD thực tế, Công ty có thể xem xét mua bổ sung các gói bảo hiểm khác cho các đối tượng gắn bó và có thâm niên làm việc tại Công ty như bảo hiểm sức khỏe, bảo hiểm hưu trí,…Chế độ đào tạo: Tất cả người lao động đều được tham gia các lớp đào tạo liên quan đến tìm hiểu môi trường làm việc, hội nhập với Công ty cũng như các nội dung đào tạo khác để nâng cao trình độ, đáp ứng yêu cầu công việc được giao.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công ty TNHH Gameloft Vietnam",
  "mo_ta_cong_viec": "C++ programming & OPP knowledgeAndroid PortingGame features in Gameloft gamesAfter the initial training period, the intern will join on-the-job training - work directly with the team on practical projectsProposing ideas to contribute to the development of the team, department and studio in general",
  "yeu_cau_cong_viec": "Final year students from IT Universities; able to work full-time or at least 4 days/week for 6 monthsC++ programming & OOP knowledgeGood logical thinking & willingness to learnHave a passion for programming, especially mobile game programmingEnglish proficiency is an advantage;Local Vietnamese candidates only",
  "quyen_loi": "An allowance of 6,000,000 VND gross/monthProfessional training to fully develop your potentialA creative, modern and open working place with our talents from around the worldWork hard, play hard and enjoy various activities (team building, events, CSR, etc)The opportunity to become an official employee of GameloftInternship-from-home is available during times of Covid-19Electricity/Internet allowance during WFH situation: 250,000VND/month",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN VUA NỆM",
  "mo_ta_cong_viec": "- Cập nhật, xây dựng nội dung Website thường xuyên theo kế hoạch cụ thể- Phối hợp cùng team phát triển nội dung web.",
  "yeu_cau_cong_viec": "- Sinh viên năm 3, năm 4 các trường Đại Học chuyên ngành kinh tế, marketing, công nghệ thông tin.- Có thể làm việc full-time (thứ 2 - thứ 6) hoặc tối thiểu 3 buổi/tuần- Khả năng tìm hiểu nghiệp vụ tốt, tiếp thu nhanh, sáng tạo, tư duy logic tốt.- Có khả năng quản lý, lập kế hoạch tốt- Trung thực, cẩn thận, tỉ mỉ",
  "quyen_loi": "- Được hỗ trợ dấu thực tập- Có cơ hội trở thành nhân viên chính thức- Được cầm tay chỉ việc, đào tạo 1-1 các kỹ năng, kinh nghiệm làm việc- Được làm việc trong môi trường chuyên nghiệp, trẻ trung, năng động- Trải nghiệm dự án thách thức lớn , chất lượng cao để phát triển bản thân- Tham gia các hoạt động vui chơi giải trí, teabreak cuối tuần.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN VUA NỆM",
  "mo_ta_cong_viec": "- Phối hợp công việc với các bộ phận phát triển website trong quá trình xây dựng phần mềm- Kiểm thử các tính năng được yêu cầu- Tham gia họp, hỗ trợ đội ngũ phát triển sản phẩm cập nhật tài liệu khi có yêu cầu mới- Tham gia review các tài liệu thiết kế giao diện, thiết kế kỹ thuật để nắm bắt tốt nhất các chức năng của hệ thống, phát hiện sớm các vấn đề ngay từ giai đoạn thiết kế, phát triển.- Phối hợp cùng team phát triển nội dung web.",
  "yeu_cau_cong_viec": "- Sinh viên năm 3 trở đi của các trường đại học, cao đẳng chuyên ngành CNTT, hệ thống thông tin kinh tế.- Có thể làm việc fulltime (thứ 2 - thứ 6) hoặc tối thiểu 3 buổi/tuần- Khả năng tìm hiểu nghiệp vụ tốt, tiếp thu nhanh, sáng tạo, tư duy logic tốt.- Có khả năng quản lý, lập kế hoạch tốt- Trung thực, cẩn thận, tỉ mỉ",
  "quyen_loi": "- Được hỗ trợ dấu thực tập- Có cơ hội trở thành nhân viên chính thức- Được cầm tay chỉ việc, đào tạo 1-1 các kỹ năng, kinh nghiệm làm việc- Được làm việc trong môi trường chuyên nghiệp, trẻ trung, năng động- Trải nghiệm dự án thách thức lớn , chất lượng cao để phát triển bản thân- Tham gia các hoạt động vui chơi giải trí, teabreak cuối tuần.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH SAMSUNG SDS VIỆT NAM",
  "mo_ta_cong_viec": "• Diễn giải và thực hiện các tiêu chuẩn đảm bảo chất lượng nhóm vận hành hệ thống (Sever(OS/DB)/Network).• Lập kế hoạch, tiến hành giám sát việc đánh giá và kiểm tra quá trình hoạt động đảmbảo chất lượng.• Khuyến nghị và phát triển các phương án khắc phục và phòng ngừa rủi ro trong các hoạt động đảm bảo chất lượng.• Báo cáo, trao đổi với Headquater để cùng lên kế hoạch đào tạo cho các nhóm phát triển và vận hành về đáp ứng tiêu chuẩn chất lượng.",
  "yeu_cau_cong_viec": "• Ứng viên học chuyên ngành IT ở đại học hoặc ứng viên có kinh nghiệm IT.• Ưu tiên người có kinh nghiệm QA từ 1 năm trở lên.• Ưu tiên người có khả năng giao tiếp tiếng Hàn (Yêu cầu không bắt buộc).",
  "quyen_loi": "• 3 lần thưởng trên năm, đánh giá tăng lương đình kỳ hàng năm.• Trợ cấp chứng chỉ Topik hàng tháng (lên tới 6tr/tháng).• Phụ cấp ăn trưa: 1,2tr/ tháng.• Thử việc 02 tháng hưởng 100% tiền lương.• Đóng bảo hiểm full lương (kể cả trong 2 tháng thử việc).• Môi trường thuận lợi để duy trì và phát triển ngoại ngữ tiếng Anh.• Cơ hội tham gia các dự án quy mô lớn, trực tiếp làm việc với các chuyên gia đầu ngành lĩnh việc IT trong nước và Hàn Quốc.• Khai phá tiềm năng với các khoa đào tạo chuyên sâu về chuyên môn, hội thảo, khóa học theo nguyện vọng cá nhân, Công ty trợ cấp lên tới 1000$/ năm.• Tài khoản LinkedIN Learning với các khóa học không giới hạn số lượng.• Công việc có nhiều thách thức giúp rèn luyện chuyên môn và nâng cao năng lực.• Tiếp cận với những cơ hội thăng tiến hấp dẫn.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/09/2022"
},
{
  "name": "Công ty Cổ phần Công nghệ phần mềm và quảng cáo trực tuyến MegaAds",
  "mo_ta_cong_viec": "• Triển khai các chiến dịch quảng cáo cho mobile app/game trên các nền tảng: Google Ads, Facebook Ads, Apple Search Ads, Unity Ads,...• Nghiên cứu, tối ưu từ khóa của app/game trên kho ứng dụng Google Play và App Store.• Tìm kiếm, nghiên cứu, phân tích, đánh giá thị trường tiềm năng và lên chiến lược marketing cho app/game.• Nắm bắt xu hướng thị trường, kết hợp với nghiên cứu đặc điểm và hành vi của khách hàng để sáng tạo ra các nội dung quảng cáo hiệu quả.• Sử dụng dữ liệu và A/B tetsing để phân tích hành vi người dùng, đo đếm các chỉ số về CPI, LTV hoặc ROAs,… tối ưu hóa các chiến dịch marketing.• Tham gia định hướng, phối hợp phát triển app/game cùng đội developer.• Lập báo cáo hiệu quả của hoạt động quảng cáo marketing.",
  "yeu_cau_cong_viec": "• Tư duy về phân tích dữ liệu và tính logic.• Tiếng Anh có thể sử dụng trong công việc.• Trên 2 năm kinh nghiệm trong lĩnh vực digital marketing trong mảng mobile game.• Có kinh nghiệm làm việc với dữ liệu và phân tích hành vi người dùng.• Có khả năng quản lý và xử lý nhiều chiến dịch cùng một lúc.",
  "quyen_loi": "Lương cứng cạnh tranh thỏa thuận upto+ phụ cấp ăn trưa 30k/ ngày. Chế độ thưởng lên tới 30% lợi nhuận game về cho team game.Môi trường làm việc thoải mái, năng động, thời gian làm việc phù hợp cho những hoạt động cá nhân. (8h30-17h thứ 2 đến hết sáng thứ 7)Nghỉ phép năm không hết sẽ được hoàn tiền.Tăng lương hàng năm theo năng lực làm việcThưởng hàng tháng theo dự án.Khám sức khỏe hàng năm. Đầy đủ chế độ về BHXHDu lịch hàng năm vào mùa hè, teambuilding cuối năm, tổng kết cuối năm, liên hoan kỷ niệm sinh nhật công ty…Thưởng lễ tết (thưởng 2/9, tết dương lịch, tết lao động, tết âm lịch).Quà sinh nhật, quà tết, quà các ngày đặc biệt, quà cưới….",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 17/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN ĐẦU TƯ CHÂU Á - THÁI BÌNH DƯƠNG",
  "mo_ta_cong_viec": "Trực tiếp tham gia phát triển phần mềm cho Tập đoàn/công ty trong các lĩnh vực: Chứng khoán/FinTech, Du lịch & Khách sạn, Xây dựng, Doanh nghiệp, ...Cung cấp sản phẩm ứng dụng với số lượng giao dịch rất lớn, đòi hỏi hiệu năng xử lý caoXây dựng các hệ thống phần mềm cho các lĩnh vực trong/ ngoài nước mà Apec Group đầu tưTham gia làm rõ nghiệp vụ, thiết kế giải pháp, phát triển nâng cấp hệ thống theo yêu cầuTham gia review thiết kế, review code, tối ưu hệ thống đáp ứng lưu lượng truy cập caoNghiên cứu áp dụng công nghệ mới nâng cao chất lượng, tối ưu nguồn lực phát triển",
  "yeu_cau_cong_viec": "Ứng viên có từ 02 năm kinh nghiệm trở lên trong ngôn ngữ lập trình C# (.Net)Tư duy về thiết kế hướng đối tượng và nắm vững kiến thức về cấu trúc dữ liệu và giải thuật, lập trình hướng đối tượng ...Thành thạo SQL, PLSQL, có kiến thức về các hệ quản trị cơ sở dữ liệu Oracle/MySQL, noSQL, có khả năng tối ưu CSDLƯu tiên ứng viên có kiến thức tổng quan về các lĩnh vực Du lịch, khách sạn, nhà hàng, nghỉ dưỡng,...",
  "quyen_loi": "Thu nhập cạnh tranh lên đến 2,000$, thỏa thuận xứng đáng với năng lực ứng viên.Điều chỉnh lương tối thiểu 2 lần/ năm + Phụ cấp ăn ca + Thưởng lễ tết, thưởng quý, thưởng cuối năm, lương tháng thứ 13+++Văn hóa trẻ trung, sáng tạo với các hoạt động nội bộ (du lịch, team building,…), các CLB thể thao, máy tập gym, game Table football,...Được hưởng đầy đủ các chế độ bảo hiểm & phúc lợi theo quy định của Nhà nước và được hưởng thêm các chính sách đãi ngộ dành riêng cho CBCNV của Tập đoànLàm việc tại văn phòng đẹp, sáng tạo và thân thiện với môi trường do chính những thế hệ trẻ của Apec thiết kế",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN TRUYỀN THÔNG DELEMENTS",
  "mo_ta_cong_viec": "Xây dựng ứng dụng web Về Backend:- Xây dựng Cở sở dữ liệu (Data base)- Lập trình xây dựng các dịch vụ Web API- Lập trình xử lý dữ liệu (chuyển đổi, cập nhật, lưu trữ)- Lập trình xử lý dữ liệu bản đồ (dữ liệu không gian)Về Frontend:- Xây dựng giao diện web cho người dùng- Tham gia các dự án phát triển và tích hợp phần mềm khác theo yêu cầu",
  "yeu_cau_cong_viec": "- Có kinh nghiệm lập trình C- Có kinh nghiệm Fullstack, lập trình web đảm bảo UX/UI, server hosting SEO.- Biết wordpress, webflow và các nền tảng tương tự là 1 lợi thế- Tốt nghiệp Cao đẳng trở lên, có kinh nghiệm làm việc trong lĩnh vực thời trang.- Có kỹ năng quản lý, sắp xếp công việc- Giao tiếp tiếng anh cơ bản",
  "quyen_loi": "- Lương thỏa thuận- Thưởng tháng 13 + Thưởng hiệu quả công việc + Tăng lương theo năng lực- Môi trường làm việc thân thiện- Cơ hội thăng tiến cao cùng sự phát triển của Công ty- Công việc ổn định, lâu dài- Được hưởng các chế độ theo quy định của Nhà nước.- Tham gia các sự kiện thời trang & team building của công ty.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN ĐẦU TƯ CHÂU Á - THÁI BÌNH DƯƠNG",
  "mo_ta_cong_viec": "Trực tiếp tham gia phát triển phần mềm cho Tập đoàn/công ty trong các lĩnh vực: Chứng khoán/FinTech, Du lịch & Khách sạn, Xây dựng, Doanh nghiệp, ...Tham gia phân tích, thiết kế luồng phát triển của ứng dụng di động dựa vào yêu cầu đã phân tích từ BA.Đánh giá, phân tích, nâng cấp và tối ưu mã nguồn trong quá trình phát triển.Nghiên cứu các công nghệ mới để áp dụng trong các dự án hiện tại và tương lai.Tham gia đưa ra những ý tưởng, giải pháp mới cải thiện công việc cũng như góp phần tăng doanh thu cho công ty",
  "yeu_cau_cong_viec": "Ít nhất 01 năm kinh nghiệm phát triển ứng dụng di động React Native sử dụng ngôn ngữ lập trình javaScript bao gồm ES6,7,TypeScript.Có kinh nghiệm về vòng đời ứng dụng React Native, sử dụng thành thạo các componet của React, có hiểu biết Redux/ Redux Saga, Redux Thunk, UnitTest.Có kinh nghiệm làm việc về các thư viện như Google Map, FaceBookSDK, Google SDK. Tích hợp các cổng thanh toán lớn là một lợi thế.Có kinh nghiệm lập trình ứng dụng native sử dụng Android (Kotlin, Java)Có kinh nghiệm tích hợp các RESTful API, Web service, Web socket,Firebase và các SDK, thư viện trong quá trình phát triển ứng dụng.Có kiến thức về cấu trúc dữ liệu, giải thuật, lập trình hướng đối tượng.Thành thạo sử dụng Git/SVN để quản lý mã nguồn.Có kinh nghiệm test, debug và tối ưu hiệu năng cho ứng dụng.Có kinh nghiệm làm việc, quản lý nhóm sử dụng Agile/Scrum.Có kinh nghiệm sử dung và làm việc với các hệ quản trị CSDL như Oracle, MySQL, Maria DB, MS SQL là một lợi thế.",
  "quyen_loi": "Thu nhập cạnh tranh lên đến 1,500$, thỏa thuận xứng đáng với năng lực ứng viên.Điều chỉnh lương tối thiểu 2 lần/ năm + Phụ cấp ăn ca + Thưởng lễ tết, thưởng quý, thưởng cuối năm, lương tháng thứ 13+++Văn hóa trẻ trung, sáng tạo với các hoạt động nội bộ (du lịch, team building,…), các CLB thể thao, máy tập gym, game Table football,...Được hưởng đầy đủ các chế độ bảo hiểm & phúc lợi theo quy định của Nhà nước và được hưởng thêm các chính sách đãi ngộ dành riêng cho CBCNV của Tập đoànLàm việc tại văn phòng đẹp, sáng tạo và thân thiện với môi trường do chính những thế hệ trẻ của Apec thiết kế",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "Công ty TNHH Phần mềm Nhân Hòa",
  "mo_ta_cong_viec": "- Tham gia phân tích yêu cầu, thiết kế tính năng, lập trình trong các dự án phát triển sản phẩm trên nền Vuejs, ReactJS.- Nghiên cứu và xây dựng phát triển các sản phẩm mới ứng dụng cho khách hàng- Thiết kế, phát triển và maintain cho backend code theo hướng API- Làm việc, phối hợp công việc theo nhóm dưới sự phân công công việc của cấp trên",
  "yeu_cau_cong_viec": "- Có kinh nghiệm lập trình từ 1 năm trở lên.- Có kiến thức về lập trình hướng đối tượng.- Có khả năng đọc hiểu tài liệu tiếng Anh chuyên ngành.- Có kỹ năng phân tích và giải quyết vấn đề.- Có tinh thần học hỏi, cẩn thận, trách nhiệm với công việc.- Có khả năng làm việc độc lập và theo nhóm.Frontend Developer:- Có kinh nghiệm xây dựng website sử dụng HTML, CSS, Javascript.- Sử dụng thành thạo 1 trong các framework: VueJS, ReactBackend Developer:- Sử dụng thành thạo 1 trong các framework: Django, Flask.- Có kinh nghiệm làm việc với các database MySQL, MongoDB.- Có kinh nghiệm triển khai và phát triển ứng dung qua API.- Có kinh nghiệm sử dụng và giải quyết vấn đề đối với các hệ thống Linux.- Có hiểu biết Cloud Openstack, ảo hoá (QEMU/KVM) là một lợi thế.- Có kinh nghiệm về Docker/Container là một lợi thế.- Hiểu biết cơ chế Load Balancing, Clustering; xây dựng hệ thống High Availablity là một lợi thế.",
  "quyen_loi": "- Tham gia đầy đủ các chế độ BHXH, BHYT, BHTN theo quy định pháp luật và quy định của Công ty. Hưởng các chế độ thưởng lễ tết.- Có phụ cấp đi lại, ăn trưa, điện thoại- Được xét tăng lương hàng năm/đột xuất theo năng lực làm việc.- Được đào tạo và tham gia các khóa phát triển các kỹ năng mềm theo định kỳ (kỹ năng quản lý thời gian, lắng nghe, lập kế hoạch…30 kỹ năng mềm)- Môi trường làm việc năng động, hiện đại, chuyên nghiệp và thân thiện (các công cụ làm việc hiện đại, theo quy trình chuẩn quốc tế như bitrix24…)- Có cơ hội học hỏi, phát triển kiến thức và kỹ năng chuyên môn.- Có cơ hội thăng tiến trong nghề nghiệp.- Nâng cao thu nhập cho người có năng lực, tâm huyết và gắn bó lâu dài với Công ty.- Hàng năm công ty tổ chức teambuiding, tham quan…",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "FPT Software",
  "mo_ta_cong_viec": "• Capable to do Self-managed project• Expected to be more flexible to switch or update tasks during the Sprint in Agile software development methodology• Expected to put extra time/effort and interaction with US Team members during the first few days of the assignment to get more information/domain knowledge to start the task• Can work on night shift when necessary, or upon project demand",
  "yeu_cau_cong_viec": "Must have• Proficient in Go or Java• Has working knowledge on Spring boot framework• Has AWS knowledge or has working knowledge on DynamoDB, Go Lambda, Go AWS Batch, S3, EC2, CodeCommit)• Has work experience on using Kafka, Couchbase• Knows Microservice development; REST API implementation,• Has worked experience on using MySQL, PosgreSQL, MongoDBGood to have:• Optional but an advantage: Knowledge on Polymer JS; Prometheus Alerts; Grafana; Kubernetes",
  "quyen_loi": "• “FPT care” health insurance provided by AON and is exclusive for FPT employees.• Annual Summer Vacation: follows company’s policy and starts from May every year• Salary review 2 times/year or on excellent performance• International, dynamic, friendly working environment• Annual leave, working conditions follow Vietnam labor laws.• Other allowances: lunch allowance, working on-site allowance, etc.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "FPT Software",
  "mo_ta_cong_viec": "Develop Customer TV (streaming application) on Roku devices:• Maintain, develop features (including UI features) for direct stream app on Roku devices base on provided specifications.• Write code and unit tests that are understandable and maintainable and with good performance• Debug effectively within the primary area to help find root cause• Provide helpful, timely code reviews• Collaborate professionally with teammates and peers• Communicate with engineering precision, escalating blockers quickly, clarifying requirements and sharing assumptions",
  "yeu_cau_cong_viec": "• A bachelor’s degree in computer science or equivalent understanding of computer science fundamentals and development best practices• 6+ years of professional experience working with and staying current in the latest advances in web and mobile technologies, highly preferred• Have significant software development experience on one or more native app platforms, such as iOS, Android, Fire TV or Web application (using Java / Javascript / C#)• Have significant experience working on UI development, follow UI and animation spec.• Understand best practices for integrating native app clients with cloud services• Comfortable with a variety of languages and frameworks, and willing to learn new ones.• Understand best practices for performance management and improvement in software development• Excellent debugger and problem solver.• Experience working with video streaming is a plus• Have experience developing Roku app using XML & Bright Script language is a plus",
  "quyen_loi": "• “FPT care” health insurance provided by AON and is exclusive for FPT employees.• Annual Summer Vacation: follows company’s policy and starts from May every year• Salary review 2 times/year or on excellent performance• International, dynamic, friendly working environment• Annual leave, working conditions follow Vietnam labor laws.• Other allowances: lunch allowance, working on-site allowance, etc.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CJ OLIVENETWORKS VINA CO., LTD",
  "mo_ta_cong_viec": "Operate a cosmetics online mall.Operate e-commerce systems of Taiwan, Vietnam, Korea, and Singapore in Vietnam.E-commerce experience and business understanding are required.You will contribute to the overall component design and play a key role in implementing features.Design, develop and test specific component features and functions, prepare functional specifications, and build prototypes.Works on multiple highly complex major tasks requiring innovative solutions including security, scalability, and performance requirements.Ensures proper test coverage exists based on requirements and design specifications. Write tests for existing and created code to ensure compatibility and stabilityCoaching and managing junior developers.",
  "yeu_cau_cong_viec": "Qualifications: Bachelor's Degree in IT/Computer Science or related.At least 2 - 4 years of experience software engineer.Hands-on experience working SQL knowledge and experience working with relational databases, such as MySQL or Postgres for these procedures, functions, packages.Comprehend Web application development by Magento and PHP.Hands-on experience implementing RESTFUL, API.Ability to communicate clearly and concisely, both orally and in writing, as an advocate for technology solutions.Eager to seek self-improvement, manager’s feedback on personal’s performances every month.Strong analytical and problem-solving skills, with proven ability to design pragmatic solutions.Experience with online mall systems, e-commerce.Experience in online malls or e-commerce is a plus.CI, pair programming, Agile, Jenkin, PHP, opensource.Experience in design patterns, SOLID design, clean code.Experience from scratch with setting up JBoss Application Server, Tomcat serverGreat work ethic.",
  "quyen_loi": "Annual medical Checking (~USD5,000 per year)BSH Insurance;Discount for CJ's brands (CGV Cinema, TLJ..);Parking fee;Telephone fee;Lunch fee.Happy Hour, Football Club, English Club, and other exciting activities.Global team. We work with Vietnam, Indonesia, and Korea co-workersHave a big chance to work onsite-overseas, we use English mainly to communicate at workNot just a job, where to build your careerChallenging GDC project.Good benefits package and allowance, dinner party once a monthNice boss, flexible working style and freely speak out your ideas",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CJ OLIVENETWORKS VINA CO., LTD",
  "mo_ta_cong_viec": "Maintaining and developing NodeJs appCreate and manage several API integrationsImplementing improvements to technologies and processes.Assist with creation and development of feature requirements.",
  "yeu_cau_cong_viec": "3+ years of experience as a backend engineer working with Nodejs.Experience with using databases like PostgreSQL, MySQL, SQL Server, and Oracle.Good understanding and following of software development methodologies and release processesExperience with REST APIs.Creative thinking and good at problem-solvingHaving knowledge of CRM systems is a plus.Having knowledge of Heroku is plusExperience another language like PHP, and Java is a plus.English communication skills are neededExcellent skills in JavaScript, NodeJSCreative thinking and good at problem-solvingHaving knowledge of CRM systems is a plus.Knowing Heroku is plusExperience another language like PHP, and Java is a plus.PostgreSQLHands-on experience implementing RESTFUL, API.",
  "quyen_loi": "Annual medical Checking (~USD5,000 per year)BSH Insurance;Discount for CJ's brands (CGV Cinema, TLJ..);Parking fee;Telephone fee;Lunch fee.Happy Hour, Football Club, English Club, and other exciting activities.Global team. We work with Vietnam, Indonesia, and Korea co-workersHave a big chance to work onsite-overseas, we use English mainly to communicate at workNot just a job, where to build your careerChallenging GDC project.Good benefits package and allowance, dinner party once a month.Nice boss, flexible working style and freely speak out your ideas",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CJ OLIVENETWORKS VINA CO., LTD",
  "mo_ta_cong_viec": "Work closely with Customers to get their requirements, design solution, and workflow.Communicate with system Users and investigate and troubleshoot system problems.Develop, implement and enhance the Backoffice system for Customers.Work as part of a team and participate in the Deployment process using CI/CD.Coordinate with other members to do technical analysis and proposal, code review, and coach some software developers.",
  "yeu_cau_cong_viec": "Strong interpersonal and communications skills, both oral and written.Strong debugging and problem-solving skills.Java EE development experience.Web development knowledge and Database/SQL knowledge:+ Java 8 programming language, Spring MVC, Spring boot framework.+ Restful API+ JavaScript, ES6, JQuery, HTML/CSS, JSP.+ Oracle 12C, MySQL: Professional in PL/SQL (Procedure, Function)+ ORM: MybatisExperienced with Webserver technologies: using Jboss, Tomcat, or Httpd server.Experienced with CI/CD tools: Git/SVN source control, Hudson/Jenkins.Experienced with Linux command line.",
  "quyen_loi": "Annual medical Checking (~USD5,000 per year)BSH Insurance;Discount for CJ's brands (CGV Cinema, TLJ..);Parking fee;Telephone fee;Lunch fee.Happy Hour, Football Club, English Club, and other exciting activities.Global team. We work with Vietnam, Indonesia, and Korea co-workersHave a big chance to work onsite-overseas, we use English mainly to communicate at workNot just a job, where to build your careerChallenging GDC project.Good benefits package and allowance, dinner party once a month.Nice boss, flexible working style and freely speak out your ideas",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CÔNG TY TNHH TƯ VẤN GIẢI PHÁP SECOMM",
  "mo_ta_cong_viec": "SECOMM is looking for creative and high-skilled Senior Frontend Developers to build, develop and maintain software products for our clients in Australia, Singapore and The US.If you have a passion for technology, a proactive mindset, willing to learn and always want to improve your skill set, you are definitely the brightest we are seeking!",
  "yeu_cau_cong_viec": "Fluent and effective communication in English with foreigners.At least 2 years of commercial experience with ReactJS/NextJS and 4 years of experience as web developerGood working experience in using JavaScript, HTML5, CSS.Experience in using Typescript, Javascript, TailwindCSS, GraphQL.Proficient understanding of code version control GIT tool.",
  "quyen_loi": "Attractive salary package including allowance & insurances.Salary review every year based on employee’s performance and contribution.Working devices are provided by the companyWorking from home remotely or at office as choiceBonus subject based on staff performance.Company trip at least once a year.Employee's birthday and year-end parties.Excellent team-building activities, internal training by our talented technical leads and TechTalk sessions to help company members collaborate and grow skills every day.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "CJ OLIVENETWORKS VINA CO., LTD",
  "mo_ta_cong_viec": "Create well design background process to handle high volume of data (utilizing queueing system)Create and manage several API integrationsBuild high performance, scalable solutions using Kubernetes, AWS Lambda, and Google Cloud BigQueryContributing to our unit testing suiteEnsuring security best practices",
  "yeu_cau_cong_viec": "Development experience in a professional capacity for 2 or more yearsExperience in using Python and Flask or DjangoHave knowledge with MicroservicesExperience in using a Queue system (RabbitMQ, SNS, etc)Good knowledge & proficient in using: SQL, MySQL, PostgreSQL, or similarExperience with a cloud service provider like AWS or Google Experience with DockerProficiency in GIT using GIT flow",
  "quyen_loi": "Annual medical Checking (~USD5,000 per year)BSH Insurance;Discount for CJ's brands (CGV Cinema, TLJ..);Parking fee;Telephone fee;Lunch fee.Happy Hour, Football Club, English Club, and other exciting activities.Global team. We work with Vietnam, Indonesia, and Korea co-workersHave a big chance to work onsite-overseas, we use English mainly to communicate at workNot just a job, where to build your careerChallenging GDC project.Good benefits package and allowance, dinner party once a month.Nice boss, flexible working style and freely speak out your ideas",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công ty TNHH Gameloft Vietnam",
  "mo_ta_cong_viec": "Develop and maintain E-Commerce sites/channels that being used by million users, in daily collaboration with different internal and external partners at Gameloft.Set up/implement the technical aspects required in agreement with different business partners of Gameloft.Develop/customize different components of Gameloft online distribution systemDocument your assigned projectsReport to your direct supervisor.",
  "yeu_cau_cong_viec": "At least 1 year of working with PHP , MySQL and other web technologies (XHTML, jQuery, CSS 3, Bootstrap)Strong understanding of OOP/ OOD, design patterns and strong experienced with responsive UI is a plusExperienced with web service – RESTful, AWS (Elastic Beanstalk, RDS, Systems Manager, DynamoDB, Lambda, CloudWatch, ...), CI/CD, Nodejs.Good knowledge of SVN and Git.Familiar with web/wap programming, PHP Framework (Zend, Symfony, Laravel)Bachelor’s degree or equivalent in Information TechnologyWork accuracy, careful/responsible attitude to interact with live-op systemGood analytical and problem-solving skillsGood English (reading and writing)Self-learning and adaptability to new technologies",
  "quyen_loi": "Recruitment Process:(1) 20-minute Call. Only qualified candidates will be contacted by our recruiters,(2) Test (3-hour test),(3) 1-hour Interview,(4) Offer.Work Location and Hour:Work location: 26 Ung Van Khiem, Binh Thanh, HCMC (hybrid working model).Work hour: 08:30 A.M. - 06:00 P.M, Monday to Friday.What We Offer:An attractive salary, with Tet Holiday bonus (\"13th-month salary\"), and other performance bonuses paid every 2 quarters, or on the spot.Full coverage of SI, HI, UI, and extra insurance (PTI).A hybrid working model.A range of policies to support employees physically, mentally and emotionally while working from home.A dynamic workplace environment, with over 18 nationalities, where hundreds of world-renowned game titles (Asphalt, Minion Rush, Modern Combat, Dungeon Hunter etc.) were born.An open-space office, a cafeteria, a terrace and a Gaming Area.Other benefits from \"One of the best companies to work for in Asia 2021\" (#HRAA2021).",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "Công ty TNHH Gameloft Vietnam",
  "mo_ta_cong_viec": "Job PurposeDevelop/maintain tools, Gameloft libs support mainly for games development:Maintain, update current tools/libs to comply with clients’ requirements.Research, develop new libs based on technology trends, market’s demandSupport new platforms, stores to help game team increase working productivity with less testing time and resources, reduce unexpected errors, save time to learn new platforms.MAIN TASKSMaintain and update current online libs based on new rules/checklistCollaborate with Online Libs Lead, Deployment Lead to analyze request from Managers then research and propose development plan if technology point of view is a feasibilityPrepare detailed workflow charts and diagrams that describe input, output, and logical operation, then implement libraries.Conduct trial runs of libs to be sure it runs well and the result is correct as our expectation.Write documents about the technical aspect of libraries.Raise alarm to relevant Managers if there is any block issues; impediments that prevent tasks from reaching milestones. Report to relevant Managers on daily basis percentage completion of each task.TECHNICAL KNOWLEDGEGood knowledge of Online libraries: propose solutions whenever block issues pop up, to make sure projects can run smoothlyResearch on new technology/algorithms/methods… and communicate with related departments.RESEARCH & DOCUMENTATIONR&D on the new technology, share experiences with relevant game teams.Documentation & manuals to guide end users “how to use tools/libs effectively”CONTRIBUTION TO STUDIO:Informing game teams about upcoming changes in libraries that can affect SAI’s projects.Open workshop to help Deployment programmers know libraries workflows.",
  "yeu_cau_cong_viec": "KNOWLEDGE:Technical knowledge: C, C++, C#, Java, Lua, batch scripts, network programming, and any new technology implied by work.Good knowledge of iOS, Android, Windows platforms is a plus.Well understanding about programming patterns, algorithms and logic thinking.Good knowledge of Jenkin, git and CI/CD.SKILLS:C/C++ and JavaOptimization, code creationTeamwork, communicationDocumenting and TrainingSoftware engineeringProblem-solving, self-learning",
  "quyen_loi": "Recruitment Process:(1) 20-minute Call. Only qualified candidates will be contacted by our recruiters,(2) Test (duration is TBD, depending on your profile),(3) 1-hour Interview,(4) Offer.Work Location and Hour:Work location: 26 Ung Van Khiem, Binh Thanh, HCMC (hybrid working model).Work hour: 08:30 A.M. - 06:00 P.M, Monday to Friday.What We Offer:An attractive salary, with Tet Holiday bonus (\"13th-month salary\"), and other performance bonuses paid every 2 quarters, or on the spot.Full coverage of SI, HI, UI, and extra insurance (PTI).A hybrid working model.A range of policies to support employees physically, mentally and emotionally while working from home.A dynamic workplace environment, with over 18 nationalities, where hundreds of world-renowned game titles (Asphalt, Minion Rush, Modern Combat, Dungeon Hunter etc.) were born.An open-space office, a cafeteria, a terrace and a Gaming Area.Other benefits from \"One of the best companies to work for in Asia 2021\" (#HRAA2021).",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "Công ty TNHH Gameloft Vietnam",
  "mo_ta_cong_viec": "Job PurposeBackend Team Associate Producer is in charge of managing the entire process of evaluation, research and backend development (CMS, API,..) from the first pitch proposal to the release of any G4B stand-alone project. It includes also allocating human resources on important core task and controlling project status to ensure that new backend development meet their deadlinesAn excellent understanding of Web technical possibilities and be able to understand complex technical issuesDeep interest in high-tech and confident in your communication and your management skills",
  "yeu_cau_cong_viec": "1. Project Management and SupportHave a good understanding of Web and Cloud technical possibilitiesBe able to apprehend complex technical architecture of any G4B projects to apply backend features integration (including hosting, CMS and dashboard deployment,…) and maintenance.Be the key contact for others Game Team Producer projects about Core Backend features; communicating fluently, clearly and concisely;Be able to provide clear and complete status of the project to upper management and stakeholdersCoordinate with others project teams in order to track project’s need, timeline development, team’s productivity, formats performance and quality;Have the ability to foresee issues/risks of the different projects in development and take immediate preventive actions to avoid them;Conduct post-mortem analysis to learn from both successes and mistakes in order to improve processes and establish best practices.2. Resource ManagementOrganize brainstorming sessions with team-members and project dedicated programmers to define the core features implementationCoordinate the team wisely and pro-actively, in order to ensure smooth implementation of the assigned projects;Know team members' strengths and weaknesses, and assign suitable tasks with the Lead dev and responsibilities to the right persons, allowing them to give their best;Take care of the morale, motivation, working behavior of team members in order to make them fully committed to the project as well as to comply with studio regulations; when needed, raise issues with Department Heads and HR for suitable solutions; Organize team building activities.3. Contribution in ManagementActively raise ideas/solutions to prevent/solve problems in game production, to improve working processes, methods of management, coordination between teams (inside and outside the Studio), as well as studio organization in general;In collaboration with Department Heads and Game Team Producers, evaluate team members during evaluation periods in a constructive way, pointing out their strengths and weaknesses; identifying good elements and improve team members that are still under expectations.QualificationsGood understanding of Game Architecture Production processes; iOS and Android platforms (ex: main features, devices specifications…);Good organization and risk management skills;Be able to handle pressure and to work in a fast-paced environment with tight deadlinesResult-oriented and with positive mindset and ability to think out of the box;Open-minded attitude with flexibility of thinking;Self-disciplined, good critical thinking and excellent at problem solving;Leadership: know how to influence others in a positive way and to inspire and motivate others to higher standards of performance;Great team work and keep high demand in terms of quality of work delivered by the teams and oneselfExcellent communication skills (writing, listening and speaking);Good knowledge of the Backend Web and Cloud environment is a plus;Good understanding of digital trends and standards (web, mobile) is a plus;Experience in a creative agency with tight deadline and KPI is a plus;1 year+ experience as a Producer in game industry is a plus",
  "quyen_loi": "Recruitment Process:(1) 20-minute Call. Only qualified candidates will be contacted by our recruiters,(2) Test (duration is TBD, depending on your profile),(3) 1-hour Interview,(4) Offer.Work Location and Hour:Work location: 26 Ung Van Khiem, Binh Thanh, HCMC (hybrid working model.Work hour: 08:30 A.M. - 06:00 P.M, Monday to Friday.What We Offer:An attractive salary, with Tet Holiday bonus (\"13th-month salary\"), and other performance bonuses paid every 2 quarters, or on the spot.Full coverage of SI, HI, UI, and extra insurance (PTI).A hybrid working model.A range of policies to support employees physically, mentally and emotionally while working from home.A dynamic workplace environment, with over 18 nationalities, where hundreds of world-renowned game titles (Asphalt, Minion Rush, Modern Combat, Dungeon Hunter etc.) were born.An open-space office, a cafeteria, a terrace and a Gaming Area.Other benefits from \"One of the best companies to work for in Asia 2021\" (#HRAA2021).",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "Công ty cổ phần chuyển đổi số ADT",
  "mo_ta_cong_viec": "AIONtech là doanh nghiệp tiên phong về AIOT (Artificial Intelligence of Things – trí tuệ nhân tạo vạn vật) để tạo ra các giải pháp chuyển đổi số đột phá cho doanh nghiệp Việt Nam như: thanh toán bằng khuôn mặt, trải nghiệm khách hàng thông minh, kiosk tự phục vụ…Mô tả:●\tTổ chức thu thập, phân tích yêu cầu người dùng từ khách hàng / Quản lý●\tPhân tích nghiệp vụ để bóc tách được các logic, business rule, validation●\tChuẩn bị wireframe, mockup cho sản phẩm, POC dự án●\tViết các tài liệu đặc tả yêu cầu nghiệp vụ phần mềm, sơ đồ hóa các use case, tạo diagram●\tPhối hợp làm việc với đối tác, đội lập trình để phát triển phần mềm, website, ứng dụng●\tPhối hợp nghiệm thu, vận hành, đào tạo về sử dụng sản phẩm đã phát triển●\tPhối hợp với các bộ phận để triển khai hoạt động chung của công ty●\tTổng hợp, báo cáo theo quy định của bộ phận●\tThực hiện một số công việc khác khi có yêu cầu của cấp trênCác công nghệ của AIONtech bao gồm: AIONBank, AIONGate, AIONStore, Finki.AIONtech mong muốn tìm được các bạn trẻ với tư duy đột phá để cùng tạo nên giá trị về công nghệ cho cộng đồng, hướng tới giá trị 3T: Tử tế - Tích cực - Tiên phongThời gian làm việc: Thứ Hai đến thứ Sáu (8h30 đến 17h30) và sáng thứ Bảy (phụ thuộc tiến độ công việc)Địa chỉ làm việc: Tầng 7 - Tòa nhà PLS, 366 Nguyễn Trãi, Phường 08, Quận 5, TPHCM",
  "yeu_cau_cong_viec": "●\tKinh nghiệm BA từ 1 đến 2 năm●\tƯu tiên tốt nghiệp ngành Hệ thống thông tin hoặc có chứng chỉ liên quan●\tƯu tiên ứng viên có kinh nghiệm về kỹ thuật và các lĩnh vực khác (digital, retail, banking)Kỹ năng:●\tNgoại ngữ: Tiếng Anh (đọc hiểu và giao tiếp tốt)●\tPhần mềm: Sử dụng các công cụ vẽ wireframe, diagram, công cụ làm việc nhóm●\tPhân tích, đánh giá và đặt câu hỏi●\tGiao tiếp và truyền đạt thông tin mạch lạcThái độ:●\tCẩn thận, chăm chỉ, học hỏi nhanh, có nhiều sáng kiến.●\tChủ động trong công việc, update thông tin, kiến thức, chia sẻ kinh nghiệm…Yêu cầu khác:●\tCó khả năng đi công tác khi được yêu cầu.",
  "quyen_loi": "●\t13 - 17 triệu + Thưởng KPI●\tĐánh giá năng lực 2 lần / năm (6 tháng / lần)Phúc lợi:●\tKhông gian làm việc thoải mái, miễn phí giữ xe●\tMôi trường trẻ trung, tư duy sáng tạo với GenZ - các bạn trẻ 9x●\tĐược đào tạo và nâng cao nghiệp vụ thường xuyên●\tTham gia các hoạt động ngoài công ty: Team building, Year End Party…●\tThưởng Lễ, Tết, lương tháng 13 theo quy định●\tBHXH đầy đủ theo quy định của luật",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "Công ty TNHH Gameloft Vietnam",
  "mo_ta_cong_viec": "Data Engineer is an engaging and challenging role that requires strong understanding of mathematical models and statistical knowledge as well as passion for gaming and game design.As a Data Engineer, your main tasks would consist in :Implement all the KPI needed for Gameloft gamesAnalyze competitors Analytics solutions for ways to improve our own.Collaborate with product development teams (game or gamification solutions) to understand the insight and prioritize the analysis needsPresent information using dashboards and other data visualization techniquesPoint out bottlenecks in production",
  "yeu_cau_cong_viec": "Knowledge of and experience with reporting packages (Business Objects etc.), databases (SQL etc.), programming (XML, JavaScript, or ETL frameworks)Knowledge of statistics and experience using statistical packages for analyzing  datasets (Excel, SPSS, SAS etc.)Strong analytical skills with the ability to collect, organize, analyze, and disseminate significant amounts of information with attention to detail and accuracyBusiness Intelligence tools as Tableau or Microsoft Power BI is a plus",
  "quyen_loi": "What We Offer:An attractive salary, with Tet Holiday bonus (\"13th-month salary\"), and other performance bonuses paid every 2 quarters, or on the spot.Full coverage of SI, HI, UI, and extra insurance (PTI).A hybrid working model.A range of policies to support employees physically, mentally and emotionally while working from home.A dynamic workplace environment, with over 18 nationalities, where hundreds of world-renowned game titles (Asphalt, Minion Rush, Modern Combat, Dungeon Hunter etc.) were born.An open-space office, a cafeteria, a terrace and a Gaming Area.Other benefits from \"One of the best companies to work for in Asia 2021\" (#HRAA2021).",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 25/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN INTELLIFE",
  "mo_ta_cong_viec": "Chịu trách nhiệm chính thực hiện phát triển/triển khai các ứng dụng/hệ thống công nghệ phục vụ cho hoạt động kinh doanh, vận hành của Tập đoàn.Thực hiện việc kiểm tra, tiếp nhận các hệ thống theo các tiêu chí đã được thống nhất với đơn vị cung cấp dịch vụ.Thực hiện và giám sát việc thực hiện các hoạt động vận hành ứng dụng, quản trị & nâng cấp các hệ thống công nghệ.Tham gia xây dựng chính sách Data Governance.Tổ chức lập kế hoạch, thực hiện đánh giá kiểm soát chất lượng trong và sau khi triển khai dự ánĐịnh kỳ báo cáo tiến độ theo yêu cầuCập nhật xu hướng công nghệ phục vụ cho công việc",
  "yeu_cau_cong_viec": "Tối thiểu 02 năm làm việc trong lĩnh vực Công nghệ thông tin;Có tối thiểu 01 năm kinh nghiệm trực tiếp triển khai hoặc vận hành một trong số các nhóm giải pháp công nghệ sau hoặc tương đương:+ CRM, Digital Marketing, Customer Experience Platform, MDM, DMP & Loyalty;+ ERP, Enterprise Asset Management, Accouting, HRS;+ PMS, CRS, RMS, PoS.+ IWWMS, CMMS, Facilities Management, BIM.+ BI & Analytics, Reporting & Data warehouse.+ BPM, ESB, API Gateway;+ Contact Center, Omini Channel;+ User behavior tracking - analytics - recommendation / suggestion;+ Application Operational & Performance monitoring.Hoặc có tối thiểu 01 năm kinh nghiệm triển khai hoặc vận hành thực tế với một trong số sản phẩm công nghệ:+ Middlewere của các hãng Oracle, IBM, Microsoft, Apache hay các công cụ tích hợp dữ liệu (IBM InfoSphere, Oracle ODI, Informatica PowerCenter ... );\"",
  "quyen_loi": "Được hưởng mức thu nhập bao gồm: Lương cơ bản + Phụ cấp (ăn trưa, gửi xe,...)Được nhận các chế độ phúc lợi, đãi ngộ theo quy định (Thưởng thâm niên, Thưởng các ngày Lễ Tết, Voucher mua hàng nội bộ,...)Được xét tăng lương định kỳ 1 lần/ năm dựa trên đánh giá KPI, ASK, 360 độĐược tham gia đóng bảo hiểm ngay sau thời gian thử việcĐược làm việc trong môi trường tôn trọng và phát triển con ngườiĐược tham gia các chương trình đào tạo, phát triển năng lực chuyên mônĐược tham gia các hoạt động gắn kết, phát triển văn hóa doanh nghiệp",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 08/08/2022"
},
{
  "name": "Công ty TNHH Công nghệ thông tin và viễn thông Dolphin",
  "mo_ta_cong_viec": "Tham gia team Back-end Developer cho dự án của công tyPhân tích yêu cầu dự án, lên kế hoạch phát triển sản phẩmTriển khai các micro-services/components/APIs.Cải thiện các component của hệ thốngCác công việc khác theo phân công của quản lý",
  "yeu_cau_cong_viec": "Tốt nghiệp CĐ/ĐH ngành công nghệ thông tin hoặc liên quanCó kinh nghiệm lập trình web HTML5, CSS, JavaScript, AjaxCó ít nhất 6 tháng kinh nghiệm lập trình NodeJS (có kinh nghiệm với Laravel là một lợi thế)Đã từng làm việc với một trong những database MySQL, MSSQL, Mongo, Redis…Có kiến thức về RESTful APIs và API Communications (NATS).Có khả năng đọc hiểu tài liệu tiếng anh chuyên ngành.Có tinh thần học hỏi, tự nghiên cứu những công nghệ mới, cầu thị và gắn bó lâu dài.Có kinh nghiệm với Microservice là một lợi thế.Hòa đồng, có khả năng teamwork.",
  "quyen_loi": "Lương cứng + Lương tháng thứ 13 + thưởng các dịp lễ, tếtHưởng bảo hiểm xã hội, bảo hiểm y tế theo chế độ nhà nước ban hành.Review kết quả công việc 6 tháng một lần.Tuần làm việc 5 ngày, nghỉ T7, chủ nhật và các ngày lễ tết.Môi trường làm việc cởi mở, sẵn sàng chia sẻ, giúp đỡ lẫn nhau để cùng phát triểnKhuyến khích các thành viên trong công ty sáng tạo các ý tưởng giúp dự án, công ty phát triểnTôn trọng quyền tự do cá nhân",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN CÔNG NGHỆ HIVETECH VIỆT NAM",
  "mo_ta_cong_viec": "Xử lý hoạt động nội bộ các team và dự án, các cấp liên quanXử lý thông tin giữa nội bộ và đối tácMở rộng đối tác cung cấp dịch vụĐề xuất, làm tài liệu liên quan đến quy trình vận hànhXây dựng và duy trì các mối quan hệThực hiện các công việc phát sinh khác theo yêu cầu",
  "yeu_cau_cong_viec": "Nam nữ từ 28 – 23 tuổiTốt nghiệp trung cấp trở lênTiếng Anh giao tiếp tốt (4 kỹ năng)Chủ động, nhanh nhẹn và tính hoàn thiện caoKhả năng giao tiếp tốt, trung thực, chịu được áp lực cao trong công việcKhả năng xử lý tình huống nhạy bén, tư duy logic mạch lạc rõ ràngKỹ năng phân tích và giải quyết công việc, chú trọng kết quả và mục tiêu thời gianTính cẩn thận, trung thực và có trách nhiệm trong công việcTin học: sử dụng thành thạo MS. Office: word, excel, powerpoint",
  "quyen_loi": "Lương 18 triệu + phụ cấp + thưởngMôi trường làm việc chuyên nghiệp với mức lương thưởng hấp dẫn, đúng với năng lực của bản thânTeam buiding/du lịch hàng nămĐược hưởng các khoản BHXH, BHYT, BHTN, phép năm theo quy định của Nhà nướcThưởng Lễ, Tết theo quy định của Công tyCác khoản phụ cấp khác theo quy địnhThời gian làm việc – Từ thứ 2- thứ 7: 8h-17h15, nghỉ trưa 1h15′ tiếng",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/08/2022"
},
{
  "name": "Công ty cổ phần truyền thông Việt Nam (VCcorp)",
  "mo_ta_cong_viec": "Tiếp cận khách hàng được giao từ cấp trên, tìm khách mới khi có cơ hội.Phối hợp với khách hàng thống nhất kế hoạch đào tạo, chuẩn bị tài liệu đào tạo và đào tạo sử dụng dịch vụ cho khách hàng.Thực hiện công việc tư vấn hỗ trợ và giải đáp các vấn đề cho khách hàng qua điện thoại, livechat và xử lý ticket.Chủ động tương tác với tập khách hàng có sẵn để cung cấp thông tin, giải đáp thắc mắc và hướng dẫn khách hàng các tính năng sản phẩm và cách vận hành sản phẩm nhằm mục tiêu đẩy chỉ số active, gia hạn hợp đồng của khách hàng.Tư vấn các giải pháp giúp khách hàng vận hành giải pháp của Bizfly vào công việc kinh doanh có hiệu quả.Sử dụng linh hoạt các công cụ và phối hợp các phòng ban để giải quyết các vấn đề từ phía khách hàng một cách kịp thời và chuyên nghiệpTư vấn bán thêm, bán chéo các sản phẩm dịch vụ nằm trong hệ sinh thái của Bizfly cho khách hàng cũ.Thực hiện các công việc khác do cấp trên giao.",
  "yeu_cau_cong_viec": "● Giới tính Nam/Nữ, ưu tiên nữ●  Độ tuổi từ 22-27●  Kinh nghiệm: 6 tháng – 1 năm vị trí triển khai hoặc CSKH. Ưu tiên ứng viên nhiều kinh nghiệm.● Tốt nghiệp các chuyên ngành về kinh tế, QTKD, CNTT,….● Giao tiếp tốt, biết lắng nghe, nhẫn nại, hướng dẫn khách tận tình● Gắn bó lâu dài, có tinh thần trách nhiệm cao với công việc, kỹ năng làm việc nhóm tốt●  Ưu tiên ứng viên có kinh nghiệm làm CSKH/ dịch vụ khách hàng, có kiến thức về kỹ thuật, IT phần cứng, phần mềm. Sử dụng thành thạo kỹ năng Office.",
  "quyen_loi": "● Mức lương: Thỏa thuận;● Thưởng đạt, vượt chỉ tiêu KPI/Thưởng năng suất: Xét thưởng áp dụng khi nhân viên đạt chỉ tiêu KPI cá nhân và hoặc tùy thuộc vào tình hình kết quả kinh doanh của công ty;● Thưởng tháng lương 13 (thưởng Tết Âm Lịch): Xét thưởng định kỳ cuối năm căn cứ theo quy định của công ty và tùy thuộc vào tình hình kết quả kinh doanh của công ty;● Thưởng thâm niên: Xét thưởng định kỳ cuối năm căn cứ theo thâm niên làm việc của nhân viên theo quy định của công ty và hoặc tùy thuộc vào tình hình kết quả kinh doanh của công ty;● Thưởng Nóng, Thưởng thành tích vượt trội: Khi có thành tích xuất sắc và hoặc dự án thành công…;● Thưởng vinh danh, tôn vinh: Bình chọn giải cá nhân/bộ phận xuất sắc cấp Công ty định kỳ hàng năm;● Thưởng Tự Khoe cấp Bộ Phận: Khuyến khích CBNV, các bộ phận thi đua hoàn thành tốt các mục tiêu công việc, kích thích đổi mới, sáng tạo trong công việc; ghi nhận, động viên kịp thời các việc hay, sáng kiến hiệu quả của các các nhân, tập thể. Mức thưởng tự khoe, tự đề xuất theo quy chế và ngân sách của công ty cấp cho từng bộ phận.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY TNHH DỊCH VỤ HÀNG KHÔNG VIỆT AN",
  "mo_ta_cong_viec": "- Tham gia phát triển các dự án .NET của Công ty cho Hãng hàng không, các bên cung cấp dịch vụ du lịch- Xây dựng sản phẩm trên nền Web based- Tham gia xây dựng hệ thống Backend, API lõi cho các sản phẩm, dịch vụ của công ty.- Tham gia phân tích nghiệp vụ, tối ưu sản phẩm, đảm bảo chất lượng, tiến độ và trải nghiệm người dùng (hiệu năng, tính dễ sử dụng, cũng như mức độ ổn định của sản phẩm)- Phối hợp với team nghiên cứu và ứng dụng các công nghệ mới, giải quyết vấn đề về lượng người dùng, giao dịch lớn.- Vận hành các sản phẩm dịch vụ hiện tại.",
  "yeu_cau_cong_viec": "- Trên 1 năm kinh nghiệm về .NET- Có tư duy sáng tạo, học hỏi và tiếp thu nhanh các công nghệ mới.- Thành thạo lập trình với C#, .NET, SQL Server, Frontend skill (HTML/CSS/Javascript)- Có kỹ năng về  Javascript, Jquery, Angular, Vue JS, ReactJS là một lợi thế- Có kinh nghiệm xây dựng Webservice, SOAP/Restful API- Có kinh nghiệm hoặc muốn tìm hiểu về Data Scrapping/Crawler là một lợi thế.- Có khả năng tự tra cứu và đọc hiểu tiếng Anh chuyên ngành- Có khả năng làm việc độc lập hoặc làm việc theo nhóm",
  "quyen_loi": "- Lương từ 15 - 30 triệu- Được làm việc trong môi trường trẻ trung, năng động.- Xây dựng sản phẩm, tiếp cận các công nghệ [hiếm gặp] trong ngành Hàng không, Du lịch- Xét tăng lương 2 lần/năm- Chế độ theo luật Lao động, 24 ngày phép/năm- Tận hưởng các ưu đãi vé máy bay, du lịch hàng năm từ các đối tác Hãng hàng không của công ty",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY TNHH KAYRUS MEDIA",
  "mo_ta_cong_viec": "Thực hiện các thủ tục / quy trình kỹ thuật onboarding/offboarding nhân sự.Quản lý các account user trong công tyMua sắm các thiết bị máy móc cần thiết cho công ty.Backup dữ liệu định kỳ, thực hiện các công tác bảo trì thiết bị.Hướng dẫn nhân viên sử dụng CRM, viết document và thực hiện công tác training.Nghiên cứu các công cụ, quy trình quản lý khác, giải quyết các vấn đề, sự cố phát sinh.Vận hành các công cụ social, marketing trên Facebook, Youtube, Tiktok, website....Thực hiện các công việc khác theo sự phân công của cấp trên.",
  "yeu_cau_cong_viec": "Có kinh nghiệm ít nhất từ 1-2 năm trong lĩnh vực IT.Tuổi từ 20 – 30 tuổi, tốt nghiệp các ngành CNTT, kỹ thuật máy tính, khoa học máy tính, mạng máy tính,...Hiểu biết về hệ thống máy tính, mạng.Có kỹ năng phân tích, tổng hợp và xử lý thông tin, kỹ năng chẩn đoán và giải quyết vấn đề.Có kỹ năng giao tiếp tốt, tác phong nhanh nhẹn hoạt bát, tổ chức sắp xếp để thực hiện công việc kịp thời hợp lý.Linh động, vui vẻ, hoạt bát hòa đồng, không ngại thử thách.Khả năng đọc viết tiếng anh cơ bản.Biết về marketing là một lợi thế.",
  "quyen_loi": "Lương cứng: Thỏa thuận theo năng lực + Thưởng doanh số hiệu suất marketing.Làm càng hiệu quả thưởng càng nhiều công bằng dân chủ, thưởng lương tháng 13.Annual leave 1 ngày/ tháng, nghỉ lễ, tết, hiếu hỉ theo luật lao động hiện hành, team building, du lịch hàng năm. Được đóng BHXH, BHYT, BHTN theo quy định.Thưởng sáng kiến, đề xuất kỹ thuật… có tính ứng dụng trong thực tế.Môi trường làm việc nhiều người trẻ, năng động, vui vẻ, được tạo điều kiện để phát triển bản thân.Mỗi tháng công ty đều tổ chức ăn uống, vui chơi cho nhân viên thoải mái tinh thần, gắn kết.Góc nhỏ ăn vặt, cà phê, trà bánh, nước ngọt,… tại văn phòng dành cho nhân viên.Sinh nhật, thăm hỏi ốm đau, hiếu hỉ,…Có nhiều cơ hội thăng tiến phát triển nghề nghiệp",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty TNHH sản xuất và thương mại Ninh Thanh",
  "mo_ta_cong_viec": "- Nghiên cứu hồ sơ thầu, phụ trách việc hoàn thiện các tài liệu, hạng mục liên quan đến vấn đề kĩ thuật.- Phối hợp với các đối tác hiện có hoặc tìm kiếm đối tác mới để tìm ra các giải pháp đáp ứng nhu cầu cụ thể và phù hợp với khả năng tài chính của khách hàng- Triển khai thử nghiệm, hàng mẫu- Tham gia nghiệm thu kỹ thuật cho các dự án thương mại của công ty.",
  "yeu_cau_cong_viec": "-Có nhiệt huyết và tinh thần chủ động trong công việc.-Tốt nghiệp cao đẳng/ đại học chuyên ngành Viễn thông hoặc Công nghệ thông tin-Có kiến thức cơ bản về mạng Viễn Thông và Networking (CCNA, CCNP)-Tiếng Anh đọc, viết cơ bản- Chưa có kinh nghiệm được đào tạo.",
  "quyen_loi": "-- Thu nhập: Lương + thưởng > 15triệu / tháng (Thưởng cuối năm theo doanh thu và giá trị đóng góp cho từng dự án).- Thời gian làm việc: 8h30-17h30 từ thứ 2 đến sáng T7 hàng tuần, nghỉ lễ theo lịch nhà nước.- Đóng bảo hiểm 100% sau khi thử việc– Được công ty chi trả 100% học phí các Khóa học đăng kí bên ngoài nâng cao trình độ chuyên môn– Nghỉ mát thường niên cùng công ty 2 lần/ năm.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "Công ty TNHH Mageplaza",
  "mo_ta_cong_viec": "- Được đào tạo phát triển tính năng sản phẩm cho app trên nền tảng Shopify theo yêu cầu của Công ty.- Hỗ trợ giải quyết các vấn đề, lỗi trong quá trình khách hàng sử dụng sản phẩm và phản hồi.- Đảm bảo codes chất lượng và được tối ưu hoá.",
  "yeu_cau_cong_viec": "- Nắm vững các kiến thức về Nodejs, Reactjs.- Có trách nhiệm với công việc được giao.- Biết làm việc cá nhân và đội nhóm.- Thành thạo Tiếng Anh là một lợi thế.",
  "quyen_loi": "- Được hưởng mức trợ cấp theo quy định của công ty.- Được đào tạo miễn phí, chuyên sâu trong môi trường chuyên nghiệp.- Đào tạo 1:1 với chuyên viên cao cấp.- Trở thành nhân viên chính thức sau thời gian thực tập  với mức lương hấp dẫn.- Cung cấp máy tính cấu hình cao, 2 màn hình to (23-27\") khi làm nhân viên chính thức.- Được thử sức trong môi trường làm việc chuyên nghiệp, năng động, thử thách và nâng cao trình độ bản thân.- Được sử dụng miễn phí tất cả các tiện ích của công ty: trà, cafe, bánh kẹo, hoa quả... không gian bếp xinh đẹp sẽ giúp bạn luôn được “tẩm bổ” đầy đủ.- Tham gia các hoạt động thể thao, giải trí tại văn phòng.- Tham gia các hoạt động team- building, dã ngoại, sinh nhật thành viên, đá bóng, từ thiện, du lịch… được công ty tổ chức thường xuyên.- Được tham gia các khóa học đào tạo về kỹ năng phát triển con người.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "BÁO ĐIỆN TỬ VNEXPRESS.NET (CÔNG TY CỔ PHẦN DỊCH VỤ TRỰC TUYẾN FPT)",
  "mo_ta_cong_viec": "Lập trình và phát triển ứng dụng web trên nền tảng PHP.Nghiên cứu, phát triển và ứng dụng các công nghệ mã nguồn mở vào trong dự án.Kết hợp với các bộ phận liên quan (Kiểm thử, hệ thống…) trong quá trình phát triển dự án.Thực hiện các công việc theo yêu cầu của cấp quản lý.Thực hiện báo cáo tiến độ và tình trạng công việc cho PM và báo cáo công việc cho Manager.",
  "yeu_cau_cong_viec": "Tốt nghiệp Đại học chuyên ngành CNTT.Có ít nhất 1-2 năm kinh nghiệm lập trình PHP, Zend Framework hoặc các MVC Framework tương tự.Có kiến thức cơ bản về Html, Css, Js và MySQL.Có kiến thức và sử dụng thực tế với Caching (Memcached, Redis,...).Biết NoSQL, NodeJs, Golang ... là một lợi thế.Có khả năng làm việc độc lập, làm việc theo nhóm.Có khả năng tự nghiên cứu, tìm hiểu các công nghệ mới.Tư duy nhanh nhạy, ý thức kỷ luật cao.Có trách nhiệm trong công việc, có thể làm việc ngoài giờ.Có khả năng làm việc trong môi trường áp lực cao.",
  "quyen_loi": "- Làm việc tại – Top 100 công ty có môi trường làm việc tốt nhất Việt Nam; Báo điện tử tiếng Việt nhiều người xem nhất.- Thu nhập xứng đáng và hấp dẫn (Thu nhập bình quân từ 15-17 tháng/năm).- Thưởng tháng 13.- Thưởng sinh nhật VnExpress (1/2 tháng).- Thưởng theo hiệu quả công việc.- Chế độ nghỉ mát hàng năm (từ 4 - 6 triệu/năm).- Phụ cấp ăn trưa, xăng xe, điện thoại (1 - 1,2 triệu/tháng).- Hỗ trợ trang phục (5triệu/năm), laptop: theo quy định của công ty.- Chế độ chăm sóc sức khỏe cao cấp dành cho nhân viên và người thân (bảo hiểm cao cấp FPT care).- Chính sách đào tạo nâng cao tiếng Anh, nghiệp vụ, kỹ năng.- Các hoạt động ngoại khóa Teambuiding.- Thời gian làm việc từ thứ 2 – thứ 6.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 29/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN CÔNG NGHỆ GOWARE",
  "mo_ta_cong_viec": "Breaking down customer requirementsPropose solutions and discuss the pros and consOrganizing, and implementing the solutions agreed upon to perfectionEnsure the highest quality standard across all codebases.",
  "yeu_cau_cong_viec": "Last year, graduate students related to Information Technology or 1+ year of experience.Familiar with HTML, CSS, and Javascript.Clean/concise code writing skills.Good algorithmic thinking is a plus (NOT a must).A good UI/UX mindset is a plus (NOT a must).Knowledge of one of the online e-commerce platforms (Shopify, WooCommerce, Magento) is a plus (NOT a must).Knowledge of common front-end development tools such as Babel, Webpack, and NPM is a plus (NOT a must).Knowledge of database systems (e.g. MySQL, MongoDB), and web servers (e.g. Apache) is a plus (NOT a must).If you're still reading until here, you're qualified in Good English communication skills by default.",
  "quyen_loi": "What you'll enjoyWorking to build world-class products.Working with the latest technologies, hottest trends, and startup environment.Everything is open to discussion, from work to life.Seniors are always around for funny jokes or serious career-path advice.Opportunities for your brilliant ideas to be recognized, applied and compensated fairly.An open and honest culture where people are valued, treated fairly, trusted and empowered.Your basic benefits of working with us.CompensationInternship allowance + On-the-fly instant bonusOpportunity to become an official company member post-internshipProfit-Sharing according to company growth each yearStock Options for high-contributing individualsProfessional Working EnvironmentActive and agile working environmentFlexible working hours to prioritize your full-time education. Sometimes, we do work remotely.Investment time on Friday when we spend time learning new topics, playing with cool technologies, working on open source, brainstorming, and imagining what we can build. We learn how we learn best. From books to workshops, to make a better of ourselves for personal growth.Knowledge and expertise sharing by founders and experienced professionals in the industryMonthly knowledge sharing to expand skills and knowledge, games, and social activities with the companyAn Opportunity to participate in all types of projects you can imagineAn Opportunity to work with top-notch experts from around the worldAn Opportunity to involve in all the processes of a startup and develop technology products from scratchAn Opportunity to be in a core team of a growing startupAccess to our premium world-class technology-related events.Access to our Technology community and PropTech community.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 27/07/2022"
},
{
  "name": "Công ty CP công nghệ và truyền thông SAMO",
  "mo_ta_cong_viec": "Tham gia phát triển và xây dựng các sản phẩm dựa trên nền React NativeTìm hiểu công nghệ, xây dựng mới và phát triển tính năng hiện tại của các dự ánTham gia vào thiết kế và review source codeĐảm bảo tiến độ, chất lượng công việc và báo cáo thường xuyên tới quản lý.Trao đổi chi tiết khi phỏng vấn",
  "yeu_cau_cong_viec": "Có tối thiểu 1 năm kinh nghiệm trong lĩnh vực phát triển ứng dụng di độngCó hiểu biết và kiến thức React NativeSử dụng thành thạo các thư viện liên quan đế React Native phổ biến ( Redux, immutable, Redux-saga,..)Có kinh nghiệm trong việc tối ưu hiệu suất ứng dụng (memory usage, memory leak, cache…)Có kinh nghiệm sử dụng các thư viện Analytics và Deep link, React hooksĐã từng build thư viện react native là một lợi thếKỹ năng phân tích, tư duy logic tốt, chuyên nghiệpCẩn thận, chi tiết, có trách nhiệm cao, sẵn sàng học hỏi, chia sẻ và cải thiện",
  "quyen_loi": "Mức lương: Upto 30MMôi trường cạnh tranh, công bằng, phát huy đối đa năng lực.Tăng lương: 02 lần/năm cố định vào tháng 04 và 10 hàng năm; Tăng lương đột xuất…Chế độ bảo hiểm: BHXH, BHYT, BHTN đầy đủ theo quy định của nhà nướcKhám sức khỏe định kỳ hàng nămBảo hiểm chăm sóc sức khỏe VBI hàng năm.Thưởng đa dạng: Money Saving, thưởng tháng 13, tết âm lịch, thưởng lễ/tết, thưởng kinh Doanh cuối năm, nhân viên xuất sắc, thâm niêm, sáng kiến….Hỗ trợ tiền gửi xe, laptop, máy tính cá nhân….Thời gian làm việc: Từ thứ 2 – thứ 6; sáng thứ 7 không yêu cầu lên văn phòng chấm công.Tham gia các hoạt động: Sự kiện, hội nghị, hội thảo về Công nghệ… và các chương trình tổ chức nội bộ tại văn phòng.Chế độ đào tạo: Được tham gia các chương trình đào tạo nội bộ, chứng chỉ theo nhu cầu để phục vụ công việc đảm nhiệm.Hoạt động du lịch, nghỉ mát: 01 lần/ 1 năm. Team building: 02 lần/nămTrà, cà phê, đồ ăn nhẹ free tại văn phòng.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY TNHH ZINZA TECHNOLOGY",
  "mo_ta_cong_viec": "- Thiết kế, vận hành hệ thống trên nền tảng AWS cho khách hàng Âu Mỹ/Nhật Bản- Môi trường Development, Staging, Production- Tối ưu chi phí, performance, scaling ứng dụng trên AWS.- Quản lý, Nâng cấp, Monitoring hệ thống web/app server , Storage,...",
  "yeu_cau_cong_viec": "- Có tối thiểu 2 năm kinh nghiệm về Devops trên AWS. Đã từng làm việc với các service sau :EC2, S3, VPC, RDS, LB , SQS , Route53, SecretManager, CloudFront,IAM, Beanstalk(optional), AWS Fargate...- Có kiến thức tốt về Linux OS (Ubuntu, Centos ...), Docker- Kinh nghiệm sử dụng các tools (Ansible,Terraform,CloudFormation)- Có kinh nghiệm làm việc với (Apache, Nginx, HAProxy ....), Db : Postgresql , Mysql- Kinh nghiệm Monitoring (CloudWatch , Datadog ....)- Khả năng teamwork, communicate ( chat tiếng anh ), phân tích và giải quyết vấn đề tốt .- Có kinh nghiệm làm CI/CD (Github , Gitlab... )- Trường hợp hệ thống có vấn đề gấp cần xử lý thì sẵn sàng hỗ trợ- Nhiệt tình trong công việc và chủ động trao đổi, sẵn sàng học hỏi những công nghệ mới thông qua đào tạo và tự học- Hoà đồng, có tinh thần trách nhiệm cao với công việc, sẵn sàng hợp tác cùng với mọi người để hoàn thành mục tiêu chung.Điểm cộng :- Có thể giao tiếp tiếng anh là một lợi thế- Có chứng chỉ AWS là một lợi thế- Có kinh nghiệm làm việc với on-premise (Vmware, KVM) là một lợi thế- Có kiến thức Kubernetes là một lợi thế",
  "quyen_loi": "I./Chế độ nhân sự dành cho nhân viên chính thức trong công ty ZinZa Technology hiện tại như sau:1. Công ty cung cấp thiết bị làm việc cho toàn bộ nhân viên chính thức (bao gồm thử việc)2. Tổng thu nhập một năm: 14++ tháng lương3. Join vào dự án ODC. Khi join dự án bắt đầu từ tháng thứ 4 trở lên:- Trợ cấp ODC (team leader): 1M/tháng.- Trợ cấp ODC (member): 700k/tháng4. Trợ cấp tiếng Nhật, và các chứng chỉ IT liên quan (hình thức: trợ cấp hàng tháng, hỗ trợ chi phí thi, tăng lương...)5. Thưởng thâm niên cho các nhân sự làm việc tại công ty từ 2 năm trở lên. Mức thưởng cụ thểnhư sau:- Nhân viên có 2 năm thâm niên làm việc tại công ty: 2,000,000vnd- Nhân viên có 3 năm thâm niên làm việc tại công ty: 4,000,000vnd- Nhân viên có 4 năm thâm niên làm việc tại công ty: 6,000,000vnd- Nhân viên có từ 5 năm thâm niên làm việc tại công ty: 10,000,000vnd.6. Xét tăng lương theo năng lực và kết quả công việc: 2 lần/năm (T6 và T12)7. Được tham gia các Câu lạc bộ dưới sự tài trợ chính thức của Công ty: CLB Bóng đá, các CLB Game, Hobby, tham gia các bữa tiệc sinh nhật, team building hàng quý, hoạt động ngoại khóa của công ty ...8. Có cơ hội được onsite tại thị trường Nhật Bản.9. Thời gian làm việc: từ thứ 2 đến thứ 6 từ 8h30 - 17h30 (Nghỉ thứ 7, CN). Thời gian làm việc linh động10. Môi trường làm việc chuyên nghiệp, cởi mở, thân thiện.11. Cơ hội thăng tiến cao trong môi trường tăng trưởng liên tục12. Du lịch 2 lần/năm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/10/2022"
},
{
  "name": "Công ty Cổ phần VINID",
  "mo_ta_cong_viec": "About One Mount Real Estate UI/UX Design TeamAt One Mount Real Estate, we are trying to become the strongest Product Design team in Vietnam by focusing on MAKING IMPACT, MOVING FAST, and BEING OUTSTANDING.We like creative hustlers, people who can think outside the box, are self-motivated and get stuff done even if it seems impossible. We work fast, push the boundaries, try new things, and sometimes they don’t work, so we embrace failure and lifelong learning.Does the prospect of working with One Mount Real Estate get you charged up? If so, the Product Design team is suitable for you!RESPONSIBILTIES:You will collaborate daily with a diverse set of specialists, including Product Owners, Product Managers, Engineers, Product Analysts, Business Stakeholders & End users to build a great user experience that balances business results with end-user delight.The Day-to-day activitiesUnderstand the full scope of a typical user-centered design process: build low & high fidelity wireframes (UX), create visual design (UI) & prototype design solutions (Interaction Design).Turn data from the market, industry trends, competitive analysis, and user experience research into user insights and make the appropriate trade-offs from there.Ensure that quality of implementation meets design requirementsCollaborate and work across functions including design, product, engineering, and data teams to ship high-quality productsCollaborate with peers in other design teams and contribute to Design System",
  "yeu_cau_cong_viec": "The must-haves:Background knowledge or passion about product design, user experience, psychology...Good eye for visual design and hands-on experience in user interface design.Familiar with data and able to identify problem areas, further map out the user journey, and break these problems into smaller chunks.Able to communicate well with teams to present your design ideas and decisions clearlyExperienced with using Figma (or willing to learn new tools if you have not)A portfolio demonstrating your design skills and collaborative processAn owner’s mindset - you don’t shy away from the hard stuff.Our missions are very challenging, Dare you…Join us to build up the Best Product Design Team in VietnamJoin us to make a better life for Vietnamese users",
  "quyen_loi": "ATTRACTIVE BENEFIT PACKAGE FOR ONE MOUNT MEMBER (YOU'LL LOVE IT)Salary & Allowances:Competitive income with 100% salary on probation, lunch allowance, 13 fixed months salary, performance bonus and gift on special occasion.Annual leave: 15 days/year and other leaves/public holidays in accordance with the Labor Law of VietnamGood Insurance added Bao Viet premium healthcare insuranceBe provided with high performance laptop and screenCareer GrowthOpportunity to experience a great workplace where young & world-class talents work together passionatelyOpportunity to promptly boost your capability by solving challenging issues of a big tech ecosystem. It’s worth your try.Very diverse offline and online seminars & workshop provided by company, supervisors, mentors and buddiesClear and flexible career pathBe sponsored to study online courses and get certification.Working EnvironmentModern and flexible Agile Office fully equipped with gaming, yoga, gym, lunch area, personal locker, open space... No dress code, just shine your way.Learning culture, initiatives and proactive attitude are strongly encouraged at One MountTeam building, company trip and internal events each month",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 02/08/2022"
},
{
  "name": "CÔNG TY TNHH ZINZA TECHNOLOGY",
  "mo_ta_cong_viec": "- Quản lý hệ tầng mạng, tivi, máy tính, máy in, máy chiếu, máy chấm công, camera, loa, điện thoại nội bộ- Kiểm tra, lắp đặt, cài đăt, bảo trì bảo dưỡng ,thay thế thiết bị phần cứng CNTT khi hỏng hóc / mua mới- Làm việc với các NCC & phòng ban liên quan khi cần mua mới, sửa chữa, nâng cấp, bảo trì máy tính & các thiết bị văn phòng- Hỗ trợ người dùng cuối.- Thực hiện các công việc khác liên quan đến CNTT khi được yêu cầu",
  "yeu_cau_cong_viec": "Tốt nghiệp Đại học/Cao đẳng chuyên ngành CNTT độ tuổi từ 22 đến 28• Có hiểu biết về phần cứng máy tính PC / Laptop & kiến thức tốt về hệ điều hành Linux / Windows / MacOS• Có khả năng làm việc độc lập /làm việc nhóm / multi tasks• Có trách nhiệm trong công việc, Có kỹ năng lập kế hoạch và quản lý công việc• Có khả năng tự tìm tòi học hỏi, yêu thích và đam mê ứng dụng các công nghệ mới• Ưu tiên kinh nghiệm 1 năm ở vị trí hỗ trợ và khắc phục sự cố, cài đặt, quản trị và thiết lập bảo trì PC/Mạng.• Ưu tiên các bạn có chứng chỉ CCNA và LPI (hoặc các chứng chỉ tương đương)",
  "quyen_loi": "I./Chế độ nhân sự dành cho nhân viên chính thức trong công ty ZinZa Technology hiện tại như sau:1. Công ty cung cấp thiết bị làm việc cho toàn bộ nhân viên chính thức (bao gồm thử việc)2. Tổng thu nhập một năm: 14++ tháng lương3. Join vào dự án ODC. Khi join dự án bắt đầu từ tháng thứ 4 trở lên:- Trợ cấp ODC (team leader): 1M/tháng.- Trợ cấp ODC (member): 700k/tháng4. Trợ cấp tiếng Nhật, và các chứng chỉ IT liên quan (hình thức: trợ cấp hàng tháng, hỗ trợ chi phí thi, tăng lương...)5. Thưởng thâm niên cho các nhân sự làm việc tại công ty từ 2 năm trở lên. Mức thưởng cụ thểnhư sau:- Nhân viên có 2 năm thâm niên làm việc tại công ty: 2,000,000vnd- Nhân viên có 3 năm thâm niên làm việc tại công ty: 4,000,000vnd- Nhân viên có 4 năm thâm niên làm việc tại công ty: 6,000,000vnd- Nhân viên có từ 5 năm thâm niên làm việc tại công ty: 10,000,000vnd.6. Xét tăng lương theo năng lực và kết quả công việc: 2 lần/năm (T6 và T12)7. Được tham gia các Câu lạc bộ dưới sự tài trợ chính thức của Công ty: CLB Bóng đá, các CLB Game, Hobby, tham gia các bữa tiệc sinh nhật, team building hàng quý, hoạt động ngoại khóa của công ty ...8. Có cơ hội được onsite tại thị trường Nhật Bản.9. Thời gian làm việc: từ thứ 2 đến thứ 6 từ 8h30 - 17h30 (Nghỉ thứ 7, CN). Thời gian làm việc linh động10. Môi trường làm việc chuyên nghiệp, cởi mở, thân thiện.11. Cơ hội thăng tiến cao trong môi trường tăng trưởng liên tục12. Du lịch 2 lần/năm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/11/2022"
},
{
  "name": "Công ty TNHH Saigon Plastic Color",
  "mo_ta_cong_viec": "• Vận hành và chịu trách nhiệm các hệ thống mạng nội bộ công ty, và chi nhánh• Xử lý các sự cố về mạng.• Quản lý các thiết bị công nghệ thông tin và công nghệ của công ty.• Lên kế hoạch bảo trì, nâng cấp hệ thống, thiết bị định kỳ.• Đề xuất các phương án bảo trì, nâng cấp hệ thống, thay đổi dịch vụ theo yêu cầu phát triển của công ty.• Hỗ trợ Hành chính quản lý, bảo trì, thay thế tài sản thiết bị văn phòng.",
  "yeu_cau_cong_viec": "- Tốt nghiệp các ngành công nghệ thông tin- Chăm chỉ, nhiệt tình, chịu được áp lực- Không yêu cầu kinh nghiệm",
  "quyen_loi": "• Lương + thưởng Hấp dẫn• Tham gia đầy đủ BHXH, BHYT,...• Tham gia các chương trình đào tạo phát triển chuyên môn của công ty• Tham gia teambuilding, du lịch cùng công ty định kỳ hằng năm• Môi trường trẻ trung, năng động, chuyên nghiệp.• Chi tiết trao đổi khi phỏng vấn tuần.* Lễ/tết nghỉ theo quy định.- Công ty trang bị các phương tiện làm việc chính: Máy vi tính, văn phòng phẩm.- Các chế độ hỗ trợ khác theo chính sách Công ty.- Tuân thủ nghiêm các nội quy, quy định của Công ty. Chịu hoàn toàn trách nhiệm nếu vi phạm nội quy, quy định và bồi thường nếu có.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN BUCA",
  "mo_ta_cong_viec": "• Hỗ trợ PO trong việc khảo sát yêu cầu của khách hàng;• Viết các tài liệu đặc tả yêu cầu nghiệp vụ phần mềm, tài liệu đặc tả, trường hợp sử dụng (usecase);• Thiết kế giao diện mẫu (prototype) liên quan đến nghiệp vụ của phần mềm.• Tư vấn trên góc độ nghiệp vụ dựa vào các phân tích và nghiên cứu của mình;• Truyền đạt nội dung, hỗ trợ các thành viên dự án, quản lý dự án để làm rõ yêu cầu của khách hàng cần đáp ứng;• Phát triển bản thân để có cơ hội thử thách trở thành Team Leader trong tương lai.",
  "yeu_cau_cong_viec": "• Ưu tiên ứng viên tốt nghiệp chuyên ngành CNTT• Có kinh nghiệm làm ở vị trí tương đương tối thiểu 6 tháng – 1 năm• Có khả năng giao tiếp hiệu quả với nhóm nội bộ và khách hàng bên ngoài để thu thập và trao đổi các yêu cầu nghiệp vụ/chức năng;• Có khả năng phân tích yêu cầu và viết các tài liệu đặc tả yêu cầu;• Ưu tiên các ứng viên đã có kinh nghiệm làm việc các dự án của Khối Nhà nước.",
  "quyen_loi": "- Mức thu nhập cạnh tranh (13 - 25 triệu) theo năng lực.Thưởng dự án, thưởng lễ tết và các khoản thưởng khác...- Chế độ BHXH, BHYT, BHTN theo quy định của pháp luật hiện hành.- Tham gia các chương trình đào tạo nội bộ và đào tạo bên ngoài (Sharing, kiến thức ngành công nghệ thông tin, chuyển đổi số....).- Tham gia các chương trình teambuilding, nghỉ mát, ngày hội sinh nhật, Happy Hour, .... của công ty.· Hưởng đầy đủ các chế độ thăm hỏi sức khỏe cho bản thân và người nhà theo Chính sách đãi ngộ của Công ty;· Làm việc trong môi trường văn hóa chia sẻ, hợp tác, trẻ trung, năng động, và có cơ hội thăng tiến cao;",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "Ngân Hàng TMCP An Bình",
  "mo_ta_cong_viec": "Hỗ trợ Giám đốc Khối trong việc biên phiên dịch các tài liệu, cuộc họp liên quan.Chịu trách nhiệm theo dõi, hỗ trợ công tác nhân sự, giám sát các công việc văn bản giấy tờ, logistic và công việc hành chính khác.Hỗ trợ Giám đốc Khối theo dõi tiến độ các công việc, dự ánTham gia trực tiếp hoặc điều phối các dự án, hoạt động, sự kiện khi được yêu cầu, đảm bảo chất lượng, tiến độ và tuân thủTổng hợp, phân tích số liệu, báo cáo của Khối để thực hiện theo dõi, cập nhật tình hình kinh doanh và các thông tin khác cho Giám đốcPhối hợp theo dõi việc tổng hợp, đánh giá tình hình hoạt động vận hành, kinh doanh của các bộ phận và của Khối định kỳ hàng tuần, hàng tháng, hàng quý, kết quả năm, cũng như kế hoạch kinh doanh của Khối.Trực tiếp thực hiện các nhiệm vụ khác do Giám đốc Khối giao; báo cáo kết quả các công việc một cách chính xác và đầy đủ.",
  "yeu_cau_cong_viec": "Trình độ đại học trở lên, chuyên ngành Quản trị kinh doanh, Kinh tế, Ngoại thương, Thương mại hoặc Tài chính ngân hàngƯu tiên có từ 02 năm trong lĩnh vực ngân hàng, digital banking, fintech.Yêu cầu tiếng Anh IELTS trên 6.0, TOEIC trên 700Kỹ năng phân tích logic, tổng hợp tốt.Năng lực tổ chức sắp xếp công việc.Khả năng làm việc độc lập và theo nhóm tốt.Trung thực, thẳng thắn và trách nhiệm với công việc.Kỹ năng giao tiếp và soạn văn bản tốt.Trung thực, tin cậy, cẩn thận, kỹ năng giao tiếp tốt;Ngoại hình ưa nhìn.",
  "quyen_loi": "Mức lương cạnh tranh dựa trên Kiến thức, kinh nghiệm của mỗi cá nhân (Trao đổi khi trúng tuyển).Được hưởng chế độ Bảo hiểm theo luật lao động và chương trình ABBANK CARE (chế độ đãi ngộ, phúc lợi bổ sung dành cho toàn thể cán bộ nhân viên ABBANK).Chế độ nghỉ phép 13 ngày/năm (bao gồm 01 ngày nghỉ sinh nhật).Nơi làm việc tốt nhất Châu Á 2020 – 2021.Top 100 nhà tuyển dụng được yêu thích nhất năm 2020 – 2021 theo khảo sát từ website tuyển dụng CareerBuilder.Môi trường năng động và sáng tạo, phát huy tối đa năng lực bản thân, điều kiện làm việc tốt, đầy đủ phương tiện, thiết bị, có cơ hội tham gia đào tạo, thăng tiến, phát triển sự nghiệp.Tham gia các hoạt động văn hóa ngoại khóa (Team building, hội thao, văn nghệ...).Được vay ưu đãi (lãi suất hấp dẫn) dành cho cán bộ nhân viên ABBANK.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 30/07/2022"
},
{
  "name": "VNDIRECT",
  "mo_ta_cong_viec": "MỤC TIÊU VỊ TRÍTham gia xây dựng, phát triển và vận hành các nền tảng số hóa quy trình quản lý của các phòng ban trong Công ty.mo_ta_cong_viec1. Tham gia các dự án liên quan đến phát triển nền tảng, phần mềm- Phối hợp với các phòng ban rà soát hệ thống quản lý và làm rõ yêu cầu về phần mềm (Khối vận hành, khối Nhân sự, Khối CNTT …);- Phân tích và xây dựng mô hình, giải pháp dựa trên yêu cầu đã thu thập được;- Tư vấn dựa vào các phân tích và nghiên cứu cá nhân;- Truyền đạt nội dung, hỗ trợ các thành viên dự án để làm rõ yêu cầu cần đáp ứng;2. Xây dựng tài liệu mô tả và tham gia nghiệm thu sản phẩm- Xây dựng tài liệu đặc tả yêu cầu nghiệp vụ, thiết kế giao diện mẫu, thiết kế quản trị dữ liệu;- Xây dựng tài liệu hướng dẫn sử dụng hệ thống;- Phân tích và đánh giá ảnh hưởng tương tác giữa các Modules;- Nghiệm thu/kiểm thử sản phẩm phần mềm;3. Tổ chức hướng dẫn, hỗ trợ người dùng sản phẩm và xử lý sự cố phát sinh4. Vận hành các ứng dụng, các hệ thống đã đi vào hoạt động",
  "yeu_cau_cong_viec": "1. Trình độ học vấn:Tốt nghiệp Đại học các chuyên ngành liên quan đến Kinh tế, Tài chính – Ngân hàng, CNTT, Thống kê, Toán tin…;2. Kinh nghiệm:Từ 02 năm kinh nghiệm trở lên ở các vị trí tương đương. Ưu tiên kinh nghiệm làm việc tại các công ty trong lĩnh vực đầu tư, tài chính, chứng khoán, ngân hàng;3. Năng lực vị trí:- Hiểu biết về quy trình phát triển phần mềm Agile/ Scrum;- Sử dụng thành thạo các công cụ hỗ trợ công việc chuyên môn: Jira, công cụ thiết kế Mockup...;- Có thể đọc hiểu và giao tiếp cơ bản bằng tiếng Anh;- Năng lực tư duy, phân tích và tổng hợp;- Kỹ năng xây dựng, thiết kế và tối ưu quy trình vận hành (LEAN design);- Kỹ năng giao tiếp và trình bày;- Kỹ năng xử lý tình huống;- Kỹ năng phối hợp, làm việc nhóm.",
  "quyen_loi": "1. Cộng đồng những người làm nghề chính trực và dấn thân phụng sự- Môi trường làm nghề tài chính chuyên nghiệp- Làm việc với tinh thần làm chủ, sáng tạo và thách thức2. Thu nhập theo năng lực- Thu nhập xứng đáng theo năng lực và giá trị đóng góp- Thử việc 100% lương nếu đạt yêu cầu; xem xét thay đổi thu nhập hàng năm- Tham gia bảo hiểm sức khỏe, bảo hiểm y tế, bảo hiểm tai nạn 24/243. Tổ chức học tập và văn hóa sôi nổi- Không gian làm việc mở với trang thiết bị hiện đại- Các hoạt động văn hóa, thiện nguyện phong phú và sôi nổi",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN PHẦN MỀM CITIGO VIỆT NAM",
  "mo_ta_cong_viec": "1. Quản lý hoạt động bán hàng – Phần mềm quản lý bán hàng KiotVietTriển khai kế hoạch bán hàng tháng, quý, năm: giao nhiệm vụ, kiểm soát & hỗ trợ việc bán hàng của các nhân viên trong phòngThiết lập các mối quan hệ với các đơn vị thi công, lắp đặt, set up cửa hàng để liên kết cung cấp phần mềm quản lý bán hàng KiotViet (https://kiotviet.vn/)Chịu trách nhiệm về chỉ tiêu được giaoLiên tục sáng tạo, tìm tòi, cải thiện các phương thức bán hàng để đạt và vượt chỉ tiêu2. Quản lý nhân viênQuản lý team nhân viên kinh doanh thị trườngHỗ trợ nhân viên về mặt chuyên mônTheo dõi, đánh giá hiệu quả làm việc của nhân viên đối với mục tiêu chung của phòng và có những hỗ trợ, điều chỉnh phù hợp3. Lập kế hoạch, báo cáoLập kế hoạch bán hàng tháng, quý, năm và đề xuất phương hướng, giải pháp đến Giám đốc Kinh doanhGiám sát, phân tích các thông số về hiệu quả kinh doanh, đề xuất các giải pháp về hệ thống & chuyên môn để cải thiện hiệu quả kinh doanh4. Tuyển dụng, đào tạoPhối hợp với bộ phận Nhân sự để hỗ trợ tuyển dụng và đào tạo",
  "yeu_cau_cong_viec": "1. Học vấn, kiến thức và trình độ chuyên mônTốt nghiệp cao đẳng trở lên; ưu tiên tốt nghiệp chuyên ngành QTKD, Marketing, kế toán, CNTT hoặc chuyên ngành liên quan2. Kinh nghiệmĐã từng làm Direct sale hoặc gần nhất quản lý đội Direct sales phát triển thị trườngĐã từng quản lý team từ 8 người trở lên và quản lý tập trung tại một địa điểmSinh sống và nắm được địa bàn tại Bắc Ninh3. Những kỹ năng cần thiết cho công việcKỹ năng giao tiếp tốtCó khả năng đàm phán, thương lượngBiết cách lên kế hoạch làm việc và thực hiện kế hoạchCó khả năng đào tạo hướng dẫn các thành viên trong nhómKỹ năng sử dụng máy tính tốt, ưu tiên ưng viên đã từng làm trong lĩnh vực công nghệ",
  "quyen_loi": "- Mức lương, thưởng hấp dẫn và cạnh tranh trên thị trường( Lương cứng từ 12-27tr)- Các chính sách thưởng hiệu quả, thưởng kinh doanh, thưởng đạt KPI- Được xét duyệt tăng lương định kỳ & thưởng cuối năm theo kết quả công việc- Được hưởng các quyen_loi và chế độ theo luật quy định (Các ngày nghỉ lễ, BHXH, BHYT…)- Hưởng ngay tiền mặt các dịp Lễ, Tết, các chế độ phúc lợi từ Công đoàn- Môi trường làm việc năng động, dân chủ, minh bạch, chuyên nghiệp được trang bị đầy đủ cơ sở vật chất hiện đại- Được hưởng các quyen_loi và chính sách riêng cho nhân viên tại Citigo",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
},
{
  "name": "CÔNG TY TNHH INTELLIGENT T&E",
  "mo_ta_cong_viec": "Design and develop servicesDesign database schemaWrite clean and maintainable codeDiscuss system/software architecture with team",
  "yeu_cau_cong_viec": "At least 1 year of experience in Ruby on Rails or Golang,Knowledge of development based on API, Microservices, or Single web application.A passion for writing great, simple, clean, efficient codeBasic knowledge of RDBM (MySQL, Postgres)Basic knowledge of Frontend Technologies: JavaScript, HTML5, CSS, ReactJS, etcTask management skills, leadership skillsCommunication skills to verbally discuss technology with customers and other teammates.",
  "quyen_loi": "Great salary package. Year-end Bonus.Salary and performance review TWICE a year.MacBook is provided.A young, friendly work environment with highly-skilled team membersTraining and coaching program from our expert developers.Annual health check-ups for all staff.Self-serving coffee machine, drinks, and a pantry full of sweets and snacks.Monthly party with food and drinks.Team Building, Company Trip,... and other big events.Free language training: English and Japanese.Opportunity to go work on-site in Japan.Gifts or allowances for wedding, maternity, Women’s day, and Children DaySports clubs to maintain your balanced health: running, football, badmintonWorking Time:8:30 - 17:30 (8 hours/day, 1 hour lunch break) from Monday - Friday and the last Saturday of the month; public holidays subject to Labor Law.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 14/08/2022"
},
{
  "name": "Apero",
  "mo_ta_cong_viec": "- Phát triển ứng dụng, module ứng dụng Android theo phân phối của Team Leader- Tham gia phân tích, thiết kế kiến trúc, luồng nghiệp vụ của ứng dụng di động theo phân phối của team leader.- Phối hợp với Mid Level/Senior Developer thực hành code review- Phối hợp với các team liên quan vận hành dự án theo quy trình.- Tham gia hướng dẫn, đào tạo member mới- Được phép tự do nghiên cứu công nghệ mới, đề xuất ý tưởng đóng góp vào dự án",
  "yeu_cau_cong_viec": "- Mức lương hấp dẫn từ 10.000000 - 18.000.000VNĐ.- Được đào tạo bài bản cùng leader có nhiều năm kinh nghiệm trong phát triển mobile app- Lộ trình phát triển bản thân rõ ràng, tham gia đào tạo chuyên môn để nâng cao năng lực- Trải nghiệm dự án thách thức lớn- Xét tăng lương 2 lần/ năm.- Thưởng định kỳ 2 lần/ năm, thưởng nóng và các phúc lợi hấp dẫn.- Tham gia các hoạt động vui chơi giải trí, du lịch, team building, ăn uống cùng  thành viên trong công  ty",
  "quyen_loi": "- Có kinh nghiệm lập trình Android tối thiểu 6 tháng- Nắm được khái niệm Android cơ bản (Activity/Service/View System, Resource, Storage, Thread Handling)- Đã từng sử dụng một trong các kiến trúc MVP, MVVM- Hiểu biết Design Pattern là một lợi thế- Có khả năng dựng module độc lập là một lợi thế- Có hiểu biết về Web, Cloud technology là một lợi thế- Am hiểu Agile Scrum là một lợi thế- Đam mê, chủ động công việc, có kỹ năng làm việc nhóm, làm việc độc lập.- Đam mê phát triển sản phẩm.- Có kỹ năng làm việc nhóm/theo quy trình là một lợi thế",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 07/08/2022"
},
{
  "name": "Công ty TNHH MTV Vision Việt Nam",
  "mo_ta_cong_viec": "- Sử dụng phần mềm của công ty để để xử lí dữ liệu thô thành dữ liệu đẹp, sau đó tải dữ liệu lên hệ thống Telesales (hình thức bán hàng qua điện thoại) cho bộ phận kinh doanh bên phía Nhật Bản.- Chịu trách nhiệm hổ trợ bộ phận kinh doanh bên phía Nhật Bản khi có yêu cầu thay đổi hay bổ sung dữ liệu trên hệ thống Telesales- Sử dụng Tiếng Nhật để đọc & hiểu nội dung công việc",
  "yeu_cau_cong_viec": "- Giới tính: Nam (độ tuổi từ 20 – 30)- Tiếng Nhật giao tiếp ở mức độ trung bình N3 or N2 (không cần bằng cấp).- Chịu được áp lực và tinh thần trách nhiệm cao.- Không cần chuyên môn nhưng phải nhạy bén trong công việc và giao tiếp tốt.- Ưu tiên các ứng viên từng làm việc cho Công ty Nhật hoặc tu nghiệp sinh.",
  "quyen_loi": "- Thời gian làm việc: 08h30 - 17h30 từ thứ 2 - thứ 6 (tuy nhiên, thời gian có thể thay đổi linh hoạt, chi tiết cụ thể sẽ trao đổi trực tiếp khi phỏng vấn).- Được training bài bản ngay từ khi nhập việc- Được kí HĐLĐ thử việc và được hỗ trợ chi trả các khoản chi phí như: tiền cơm, tiền xăng, trợ cấp ngoại ngữ…- Được tham gia đầy đủ các chế độ BHXH, BHYT, BHTN khi được tuyển dụng chính thức.- Được Công ty hỗ trợ tham gia thêm gói bảo hiểm sức khỏe PVI.- Được tham gia các hoạt động tập thể do Công ty và Công đoàn tổ chức như: team building, du lịch, các CLB bóng đá, cầu lông …- Được nhận tiền mừng sinh nhật, kết hôn … theo quy định của tổ chức Công đoàn- Trong năm có 2 đợt xét duyệt nâng lương.- Môi trường làm việc thân thiện, ổn định, đảm bảo sức khỏe.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 20/09/2022"
},
{
  "name": "CÔNG TY TNHH PHÁT TRIỂN ADD-ON",
  "mo_ta_cong_viec": "Responsibilities:- Develop Full Stack .NET solutions in a distributed landscape consisting of jQuery, bootstrap, NodeJS, React, ASP.NET and click-once front-end applications.- Backend solutions consist of n-tiered .NET Framework and .NET Core implementations: technologies include RESTful APIs, WCF Services, Windows Services.- Good analytical skills with proven experience in algorithm analysis and optimization- Passionate about writing quality code and constantly honing development skills- Proven experience working in a team, as well as independently- Strong understanding of OOP, the .NET Framework and/or .NET Core, and web application development",
  "yeu_cau_cong_viec": "- Bachelor’s Degree in Information Technologies, computer sciences or equivalent- 1+ years of .NET development experience- 1+ year of Single Page Application development experience- Proficiency in SQL; advantageous, if the candidate has experience designing normalized databases Very strong technical, analytical, and problem-solving skills- Good communication in English- Good teamwork and communication skills",
  "quyen_loi": "- Flexible working time (8 hours/day and 5 days/week from Monday to Friday) and no overtime- 16 paid-leave days per year (12++ days of annual leave; 03 days of paid-sick leave and a special half day-off for 8/3 & 20/10)- Entitle 2 compensatory days off per month if the redundant working hours of previous month exceeds 16 hours- Attractive and competitive salary & bonus package (13th month salary, project bonus, business bonus, ….)- Healthcare insurance package with High level and Annual Health check-up- Opportunities to work directly with European customers- Professional, friendly, open working environment and committed talented teams- Team building activities (summer vacation, outdoor activities, weekend excursions, etc. …)- Refreshment area (foosball, ping-pong, …)",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 31/07/2022"
},
{
  "name": "DE OBELLY",
  "mo_ta_cong_viec": "- Chịu trách nhiệm về toàn bộ ấn phẩm, hình ảnh thiết kế đồ họa của thương hiệu Sohee- Thiết kế các ấn phẩm truyền thông và in ấn phục vụ các chương trình truyền thông và sale promotion, truyền thông nội bộ: Banner, Poster, Standee, Lookbook, catalogue..- Chụp ảnh Sản phẩm tại Studio của công ty,  chụp ảnh sự kiện công ty tổ chức- Thực hiện các công việc khác theo yêu cầu từ cấp trên- Lập và gửi báo cáo hàng tuần, hàng tháng theo đúng quy định.",
  "yeu_cau_cong_viec": "- Tốt nghiệp cao đẳng trở lên- Trình độ chuyên môn - kinh nghiệm:- Tối thiểu 02 năm kinh nghiệm- Thành thạo các phần mềm: Photoshop, Illustrator, InDesign- Biết chụp ảnh là một lợi thế",
  "quyen_loi": "- Được hưởng quyen_loi tương ứng với công việc đảm nhiệm và năng lực, theo qui định của Công ty.- Được trang bị thiết bị và dụng cụ để thực hiện nhu cầu của công việc.- Được đào tạo và hướng dẫn nghiệp vụ để đáp ứng yêu cầu của công việc.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 09/08/2022"
},
{
  "name": "AN NHIEN MEDIA",
  "mo_ta_cong_viec": "- Quản trị hệ thống kênh Youtube.- Tạo kênh, đăng tải video lên hệ thống kênh quản lí theo kế hoạch.- Chỉnh sửa video (Từ Nội dung Có Sẵn): Cắt, ghép, biên tập video, tạo ảnh thumbnail cho video.- Chăm sóc kênh: Comment tương tác với người xem, các nghiệp vụ promote cho video/kênh.- Phân tích các chỉ số quan trọng trong quản trị kênh: Analytics- Thu thập, phân tích, đánh giá các xu thế phát triển của nhóm chủ đề trên Youtube- Công việc khác theo sự phân công của cấp trên.Làm việc tại: 14 Phan Văn Hớn, Tân Thới Nhất, Quận 12, TPHCM (Chung Cư Proper Plaza)",
  "yeu_cau_cong_viec": "- Ứng viên trong độ tuổi 20 - 26- Biết Sử dụng Premiere, Photoshop- Có kiến thức về hệ thống Youtube là một lợi thế- Có kiến thức và khả năng tìm hiểu về khán giả ở các thị trường khác nhau đặc biệt là thị trường Mỹ là một lợi thế.- Khả năng làm việc dưới áp lực cao- Kỹ năng làm việc độc lập, làm việc nhóm- Kỹ năng tổ chức, sắp xếp công việc",
  "quyen_loi": "+ Thu nhập: 8 - 20 triệu (lương căn bản + hoa hồng + thưởng)+ Được đào tạo các kiến thức về Kiếm Tiền Trên YOUTUBE+ Được hưởng chế độ nghỉ lễ, tết và các hoạt động liên hoan+ Môi trường làm việc chuyên nghiệp, năng động.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 05/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN TẬP ĐOÀN ĐẦU TƯ CÔNG NGHỆ NAM LONG",
  "mo_ta_cong_viec": "- Tham gia nhóm Dev để xây dựng, triển khai Backend Services cho Hệ thống công ty bằng .NET Core- Sử dụng .NET Core, SQL Server- Tham gia trực tiếp vào phân tích, thiết kế, triển khai",
  "yeu_cau_cong_viec": "- Có kinh nghiệm với ngôn ngữ C# .Net Core, SQL Server.- Có kinh nghiệm làm việc với CSDL: SQL, MySQL.- Có hiểu biết về Windown Server, IIS, Swagger.",
  "quyen_loi": "- Các chính sách lương thưởng tốt, BHXH, BHYT- Được đào tạo thường xuyên- Môi trường làm việc trẻ trung, năng động, thoải mái- Nghỉ mát hàng năm",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 12/08/2022"
},
{
  "name": "CÔNG TY CỔ PHẦN TẬP ĐOÀN ĐẦU TƯ CÔNG NGHỆ NAM LONG",
  "mo_ta_cong_viec": "– Xây dựng hệ thống web sử dụng VueJs– Phát triển, cải thiện tốc độ, trải nghiệm web– Tham gia phát triển, đề xuất giải pháp kỹ thuật cho các dự án web.– Nghiên cứu, tìm hiểu các công nghệ, engine,… mới phục vụ các nhu cầu sản phẩm củɑ công ty.– Làm việc, phối hợp công việc theo nhóm dưới sự phân công công việc của cấp trên.– Phân tích thiết kế, viết tài liệu mô tả.",
  "yeu_cau_cong_viec": "- Có ít nhất 1 năm kinh nghiệm lập trình Frontend (ít nhất 6 tháng làm việc thực tế với Vuejs).– Thành thạo HTML/CSS/Javascript.– Có kinh nghiệm và tư duy tốt về Front End, UI/UX.– Có hiểu biết về server side rendering (SSR).- Khả năng làm việc nhóm, chịu áp lực công việc tốt.- Có tinh thần trách nhiệm cao, chủ động và sáng tạo trong công việc.– Nhanh nhẹn, ham học hỏi và nghiên cứu công nghệ mới tốt.– Đã sử dụng một số VueJs framework như NUXT… là 1 lợi thế.– Đã có kinh nghiệm lập trình Wordpress, lập trình với một số thư viện như Leaflet… là 1 lợi thế.– Biết thêm một trong các ngôn ngữ sau là 1 lợi thế: Nodejs, PHP, .Net, Python.",
  "quyen_loi": "- Lương và chế độ phúc lợi tốt- Đào tạo hàng tuần- Môi trường trẻ trung, linh hoạt",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 08/08/2022"
},
{
  "name": "Sunstar Vina",
  "mo_ta_cong_viec": "- Programming web (.NET), and mobile applications.- Have skills in searching and finding solutions to solve problems of software/applications.- Participate in the development and maintenance of software products.- Document and handle errors arising from software/application.- Support for installing & deploying software/applications for customers.",
  "yeu_cau_cong_viec": "- Experience in .NET, C #, and MVC.- Ability to read documents in English and communicate in English or Korean.- Experienced / proficient in web design: HTML, CSS, JS, ...- Have knowledge about SVN, Services, and API.- Have knowledge of Mysql (functions, triggers).",
  "quyen_loi": "Salary increase according to abilitySupport travel expenses according to the actual routeAble to work from home if there is an urgent needSmall and medium-sized projects will not have too much pressureDo not work overtime",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 14/08/2022"
},
{
  "name": "Công Ty Cổ Phần Tập đoàn Ominext",
  "mo_ta_cong_viec": "Hiểu và phân tích yêu cầu của khách hàng.Thiết kế test plan, test design và testcases.Thiết lập môi trường kiểm thử, thực thi và báo cáo kết quả.Quản lý, phân tích và theo dõi kết quả test, báo cáo kết quả và đánh giá chất lượng sản phẩm trước khi golive.Thực hiện các công việc khác theo sự phân công của Quản lý trực tiếp.",
  "yeu_cau_cong_viec": "Có trên 2 năm kinh nghiệm thực tế về testing.Làm việc tốt với CSDL.Nắm vững quy trình kiểm thử phần mềm.Cẩn thận, tỉ mỉ. Có tư duy logic tốt, nắm bắt nghiệp vụ nhanh, tinh thần trách nhiệm cao.Có thái độ tích cực trong công việc, có khả năng làm việc độc lập và khả năng làm theo nhóm.Lợi thế: ứng viên có kinh nghiệm lead team là 1 điểm cộng. (Không bắt buộc)",
  "quyen_loi": "Tổng thu nhập lên tới 14 tháng lương/năm với các khoản thưởng hấp dẫn khác.Lộ trình thăng tiến (Careerpath) rõ ràng, xét tăng lương/thăng chức 2 lần/năm. Được đào tạo trở thành Team Leader.Khuyến khích học hỏi thỏa sức phát triển công nghệ mới, được đào tạo về kỹ năng mềm, tham dự và đứng lớp các buổi seminar về công nghệ tổ chức nội bộ hoặc bên ngoài.Tham gia lớp đào tạo tiếng Nhật miễn phí; Trợ cấp tiếng Nhật 12 tháng liên tục lên tới 5.000.000 VNĐ.Tham gia các câu lạc bộ bên lề phong phú: CLB Thể thao, CLB Nghệ thuật, CLB Ngôn ngữ...Tổ chức thường niên sự kiện chăm lo cho con của nhân viên (quốc tế thiếu nhi 1/6, trung thu, giáng sinh, …).Du lịch 2 lần/năm vi vu cùng 500 anh em tới các vùng miền tổ quốc.quyen_loi chăm sóc sức khỏe đặc quyền với chương trình \"Bác sĩ gia đình\" dành riêng cho nhân viên của Ominext, chế độ ưu đãi khi sử dụng dịch vụ của công ty thành viên (OmiPharma).Khám sức khỏe thường niên tại bệnh viện hàng đầu của Việt Nam cùng các chế độ BHXH theo quy định của nhà nước.Thời gian làm việc linh hoạt, 8h/ngày (giờ check in tiêu chuẩn 8h00-8h45). Làm từ Thứ 2 – Thứ 6.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 08/08/2022"
},
{
  "name": "Công Ty Cổ Phần Tập đoàn Ominext",
  "mo_ta_cong_viec": "Tham gia dự án phát triển phần mềm của công ty, với vai trò BA của dự án.Hỗ trợ sales/BrSE đánh giá và phân tích nghiệp vụ, tham gia thực hiện estimate trong giai đoạn pre-sales.Khai thác và phân tích yêu cầu nghiệp vụ.Tạo tài liệu mô tả nghiệp vụ dự án (use cases, business flows, ERD,...).Đưa ra các đề xuất cho khách hàng về nghiệp vụ, giao diện và tính năng.Khai thác chi tiết về nhu cầu của khách hàng, qua đó mở rộng quy mô dự án.Quản lý sự thay đổi của yêu cầu từ phía Khách hàng và trong dự án.Tham gia kiểm thử tính đúng đắn sản phẩm trước khi bàn giao cho Khách hàng.Xây dựng tài liệu hướng dẫn sử dụng và tài liệu chuyển giao cho Khách hàng.",
  "yeu_cau_cong_viec": "Có chứng chỉ tiếng Nhật N2 trở lên, đọc viết thuần thục, nghe nói lưu loátCó kiến thức & kỹ năng cơ bản về CNTT: Cấu trúc phần mềm, cấu trúc dữ liệu, các công nghệ/ứng dụng/ nền tảng CNTT.Có kiến thức về quy trình và vòng đời phát triển phần mềm.Có kinh nghiệm test ít nhất 2 năm và đã từng làm test lead của một dự án về CNTT hoặc có ít nhất 1 năm kinh nghiệm làm BA cho các dự án CNTTCó khả năng trình bày, làm tài liệu tốt.Có tư duy tốt về phân tích hệ thống, phân tích hiệu suất.Khả năng giao tiếp, truyền đạt tốt. Logic, suy luận tốt.Có khả năng khai thác, tài liệu hoá, xây dựng các quy trình nghiệp vụ và đặc tả yêu cầuCó khả năng truyền đạt ý tưởng cho đội nhóm phát triển.Nếu chưa có kinh nghiệm BA (nhưng đạt yêu cầu trên), Công ty sẽ đào tạo và hướng dẫn. Có khả năng thiết kế database là một lợi thế.",
  "quyen_loi": "Tổng thu nhập hấp dẫn lên đến 15 tháng lương/ năm cùng với nhiều khoản thưởng hấp dẫn khác (thưởng nhân tân binh xuất sắc, thưởng nhân viên xuất sắc, thưởng nóng,…).Lộ trình thăng tiến (Careerpath) rõ ràng, xét tăng lương/thăng chức 2 lần/năm. Được đào tạo trở thành Team Leader/Manager.Tham gia lớp đào tạo tiếng Nhật miễn phí; Trợ cấp tiếng Nhật 12 tháng liên tục lên tới 5.000.000 VNĐ.Tham gia các câu lạc bộ bên lề phong phú: CLB Thể thao, CLB Nghệ thuật, CLB Ngôn ngữ….Du lịch 2 lần/năm vi vu cùng 500 anh em tới các vùng miền tổ quốc.Môi trường trẻ trung, năng động, sáng tạo và phát triển toàn diện, vượt trội cho từng thành viên.Khám sức khỏe thường niên tại bệnh viện hàng đầu của Việt Nam cùng các chế độ BHXH theo quy định của nhà nước.Văn phòng làm việc hạng A với không gian mở; khuyến khích tinh thần trẻ trung, năng động và sáng tạo.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 08/08/2022"
},
{
  "name": "Công ty Cổ phần Power Gate Việt Nam",
  "mo_ta_cong_viec": "POWERGATE GROUPđang tìm kiếm nhân tài tại vị tríNodeJS Developerđể cùng chúng tôi:Xây dựng SOFTWARE PRODUCT STUDIO Quốc tế Lớn nhất Khu vực, với 1000 thành viên (trong ~ 5 năm tới).Thực hiện sứ mệnh đưa các ý tưởng và sáng tạo đến với cuộc sống thông qua xây dựng các sản phẩm công nghệ cao cùng với các khách hàng và đối tác trên toàn cầu.Với vai trò là một NodeJS Developer, bạn sẽ:Tham gia thiết kế, xây dựng các phần mềm công nghệ cao trong vai trò là BackEnd Developer chínhĐưa các ý tưởng và sáng tạo đến với cuộc sống thông qua xây dựng các sản phẩm công nghệ cao cùng với các khách hàng và đối tác trên toàn cầu.Môi trường năng động và linh hoạt, cải thiện bản thân để trở thành một chuyên gia lập trình.Hoàn thành các dự án đúng tiến độ, chủ động học hỏi, nghiên cứu, tìm kiếm các công nghệ mới",
  "yeu_cau_cong_viec": "Tốt nghiệp Đại học chính quy chuyên ngành Công nghệ Thông tin (hoặc các ngành liên quan)Có từ  1 - 3 năm kinh nghiệm làm việc với các dự án thực tế sử dụng NodeJSCó kinh nghiệm Web API, Web Services RESTCó kiến thức cơ bản về Express - Node.js web application frameworkHiểu biết tốt về ngôn ngữ tạo server-side templateCó khả năng làm việc với cơ sở dữ liệu MySQL, PostgresQLThành thạo Git, SVN...Có khả năng tư duy logic và thuật toán tốt, phân tích và giải quyết vấn đề",
  "quyen_loi": "Nhận mức lương hấp dẫn up to 1500$ theo năng lựcThử việc hưởng 100% lươngLương tháng 13, Thưởng dự án hàng Quý (Package 14 - 16 tháng lương/năm)Lộ trình thăng tiến rõ ràng (review tăng lương 2 lần/năm)Làm việc 5 ngày/tuần (nghỉ thứ 7, chủ nhật)Làm việc trong môi trường năng động, đội ngũ nhân viên trẻ nhiệt huyếtNhiều hoạt động bonding gắn kết nhân sự hàng tháng, Teambuilding 2 lần/năm, Quỹ thưởng liên hoan team/division hàng Quý, Happy hour mỗi ngàyQuản lý Support kịp thời và hướng dẫn tận tình.Cơ hội tham gia vào ban điều hành Division và hưởng cơ chế thưởng cao theo kết quả kinh doanh của Division.Mô hình hoạt động theo cơ chế Division:Tự chủ điều hành các dự án theo mục tiêu KPIs được giao: Doanh thu, lợi nhuận, chi phí.Chủ động giao tiếp và tạo mối quan hệ tốt với khách hàng,Division phát huy được năng lực chuyên môn và Quản lý một cách cao nhất.Lộ trình phát triển rõ ràng cho từng vị trí trong các Division.",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 10/08/2022"
},
{
  "name": "Công Ty TNHH Giải Pháp Công Nghệ CIT",
  "mo_ta_cong_viec": "Xây dựng, thiết kế Web dựa trên Wordpress.Thiết kế website.  thành thạo PHP & Mysql.Biết cắt html, CSS",
  "yeu_cau_cong_viec": "- Có nghiệm ít nhất 1 năm trong lĩnh vực thiết kế website,- Biết thiết kế website theo chuẩn SEO, biết SEO là một lợi thế.- Nhiệt tình có trách nhiệm trong công việc",
  "quyen_loi": "Thu Nhập 10 -15 Triệu- Được đóng BHXH- Môi trường làm việc chuyên nghiệp, năng động nhiệt tình, hài hòa vui vẻ- Nghỉ lễ, tết theo quy định, phụ cấp trách nhiệm, cơm trưa-Cà phê hàng tuần ,  thưởng các ngày Lễ, tết, sinh nhật- 12 ngày phép năm, lương tháng 13- Thời gian làm việc: Từ thứ 2 đến thứ 7 ( 8-17h, trưa nghỉ 11h30-13h)",
  "cach_thuc_ung_tuyen": "Ứng viên nộp hồ sơ trực tuyến bằng cách bấmỨng tuyển ngaydưới đây.ỨNG TUYỂN NGAYLƯU TINHạn nộp hồ sơ: 01/08/2022"
}
]