# Core Pkg
import streamlit as st 
import streamlit.components.v1 as stc 


# Load EDA
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity,linear_kernel


# Load Our Dataset
def load_data(data):
	df = pd.read_csv(data)
	return df 


# Fxn
# Vectorize + Cosine Similarity Matrix

def vectorize_text_to_cosine_mat(data):
	count_vect = CountVectorizer()
	cv_mat = count_vect.fit_transform(data)
	# Get the cosinepip
	cosine_sim_mat = cosine_similarity(cv_mat)
	return cosine_sim_mat



# Recommendation Sys
@st.cache_data
def get_recommendation(title,cosine_sim_mat,df,num_of_rec=10):
	# indices of the course
	course_indices = pd.Series(df.index,index=df['course_title']).drop_duplicates()
	# Index of course
	idx = course_indices[title]

	# Look into the cosine matr for that index
	sim_scores =list(enumerate(cosine_sim_mat[idx]))
	sim_scores = sorted(sim_scores,key=lambda x: x[1],reverse=True)
	selected_course_indices = [i[0] for i in sim_scores[1:]]
	selected_course_scores = [i[0] for i in sim_scores[1:]]

	# Get the dataframe & title
	result_df = df.iloc[selected_course_indices]
	result_df['similarity_score'] = selected_course_scores
	final_recommended_courses = result_df[['course_title','similarity_score','url','price','num_subscribers']]
	return final_recommended_courses.head(num_of_rec)

TEMPLATE ="""
<div
style="
display: flex;
width: 80%;
justify-content: space-around;
border:2x solid red;
height:100%;
"
>
<ul>
 <li>{}</li>
</ul>

</div>
"""

RESULT_TEMP = """

<div 
style="
display:flex;
align-items:center;
justify-content:space-around;
"
>


	<div 
	style="
		
		width:70%;
		height:100%;
		margin:auto;
		padding:5px;
		position:relative;
		border-radius:5px;
		border:3px solid #98D7C2;
		box-shadow:3px 5px 15px 3px #000; 
		background-color: #167D7F;
		
		"
	>
	<h4 style="color:white; font-family:roboto;">{}</h4>
	<p style="color:white;"><span style="color:white;">📈Duration- </span>{}</p>
	<p style="color:white;"><span style="color:white;">🔗</span><a href="{}",target="_blank">Link</a></p>
	<p style="color:white;"><span style="color:white;"> Price: 💲</span>{}</p>
	<p style="color:white;"><span style="color:white;"> Enrolled: </span>{}</p>


	
	</div>
	<div
	style="
		width:25%;
		border:3px solid #016367;
		height:100%;
		font-size:1.3rem;
		box-shadow:-3px 5px 8px 3px #0A0A00; 
		display:flex;
		color:#255050;
		align-items:center;
		margin:auto;
		justify-content:space-around;
		padding-left:5px;
		border-radius:5px;
		background-color:#CFE0EA;
	"
	
	>
	<p>Require {} days to complete</p>

	</div>
</div>
"""
GRAPH_TEMP="""
<div>
<img src={} alt="hello dear" width="500" height="600">
</div>

"""
# Search For Course 
@st.cache_data
def search_term_if_not_found(term,df):
	result_df = df[df['course_title'].str.contains(term)]
	return result_df

levelWiseWeight ={'Beginner Level':1 , 'Intermediate Level':2 ,'Expert Level':3,'All Levels':3 }
def completionDays(level, total,hoursPerDay):
	# st.info(type(levelWiseWeight[level]))
	return (levelWiseWeight[level]* 2*total )//hoursPerDay

def main():

	st.title("Pathways")

	menu = ["Home","Recommend","Analysis"]
	choice = st.sidebar.selectbox("Menu",menu)

	df = load_data("udemy_course_data.csv")

	if choice == "Home":
		st.subheader("Home")
		st.dataframe(df.head(10))


	elif choice == "Recommend":
		# st.subheader("Recommend Courses")
		cosine_sim_mat = vectorize_text_to_cosine_mat(df['course_title'])
		search_term = st.text_input("Search Course")
		min, max=4, 10
		default = 5
		# default = st.number_input("6")

		num_of_rec = st.sidebar.number_input("Number of recommendations",min, max, default) #min , max , default
		num_of_days = st.sidebar.number_input("Study hours per day", 1,10,2)

		if st.button("Recommend"):
			
			if search_term is not None:
				try:
					results = get_recommendation(search_term,cosine_sim_mat,df,num_of_rec)

					with st.beta_expander("Results as JSON"):
						results_json = results.to_dict('index')
						st.write(results_json)
					
				except (Exception )as e:
					# results= "Not Found"
					# st.warning(results)
					# st.info(e)
					result_df = search_term_if_not_found(search_term,df)
					# st.info(type(num_of_days))
					if(len(result_df)==0):
						st.warning("Not found")
					else:

						st.info("Suggested Options include")
						# st.info(result_df)
						limit = num_of_rec
						for row in result_df.iterrows():
							if(limit ==0):
								break

							limit-=1
							rec_title = row[1][1]
							rec_duration = row[1][9]
							rec_url = row[1][2]
							rec_level= row[1][8]
							rec_price = row[1][4]
							rec_num_sub = row[1][5]
							level = row[1][8]
							# st.info(type(level))
							
							hours = int(rec_duration.split(" ")[0].split('.')[0])
							# st.info(rec_duration.split(" ")[1])
							if(rec_duration.split(" ")[1]=="mins"):
								hours //=60
							
							# st.info(hours)
							requiredDays = completionDays(level, hours, num_of_days)
							
							stc.html(RESULT_TEMP.format(rec_title,rec_duration,rec_url,rec_price,rec_num_sub, requiredDays),height=400)
						
						# required = min(len(result_df),int(num_of_rec))
						st.dataframe(result_df[0:num_of_rec])

	else:
		st.subheader("Analysis")
		# st.text("Built with Streamlit & Pandas")
		st.image("images/subs.jpg",caption="Distribution of Subjects")
		st.image("images/subVsStud.jpg",caption="Number of Subscribers per Subjects")
		st.image("images/courseVsLevel.jpg",caption="Distribution of Course Per level")
		st.image("images/subInLevel.jpg",caption="Subjects in each level")
		# st.image("images/priceVsSub.jpg",caption="Price vs number of Subscribers")
		st.image("images/priceInfluence.jpg",caption="Does price influence Subscription per Subject Category")
		




if __name__ == "__main__":
    main()

