import pypyodbc 
import pandas as pd
from datetime import datetime,timedelta


cnxn = pypyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=WIN-8FBERPLQ754;"
                        "Database=NewsApp;"
                        "uid=Michal;pwd=Fotades1")



command ='select top 100  Article_ID,Url, SourceType_ID,Title,ImageUrl,ReleasedDate from dbo.[Article] WHERE Downloaded = 1'
articles = pd.read_sql_query(command, cnxn)
print(datetime.now())
def get_content(article):
    command="select [Text] from dbo.[Paragraph] WHERE Article_ID="+str(article["article_id"])
    paragraphs=pd.read_sql_query(command, cnxn)
    return ' '.join(paragraphs["text"].values)


articles['content'] = articles.apply(lambda row: get_content(row),axis=1)

print(datetime.now())