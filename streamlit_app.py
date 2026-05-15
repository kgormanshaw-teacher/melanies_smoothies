# Import python packages.
import os
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session

st.write("st.secrets keys:", list(st.secrets.keys()) if hasattr(st, "secrets") else "no st.secrets")
st.stop()

# Write directly to the app.
st.title(f"Customize Your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be ", name_on_order)
# option = st.selectbox(
#     "What is your favourite fruit?",
#     ("Banana", "Strawberries", "Peaches"),
# )

# st.write("Your favourite fruit is:", option)

secrets = st.secrets.get("snowflake", {}) if hasattr(st, "secrets") else {}
connection_parameters = {
    "user": secrets.get("user") or os.getenv("SNOWFLAKE_USER"),
    "password": secrets.get("password") or os.getenv("SNOWFLAKE_PASSWORD"),
    "account": secrets.get("account") or os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": secrets.get("warehouse") or os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": secrets.get("database") or os.getenv("SNOWFLAKE_DATABASE"),
    "schema": secrets.get("schema") or os.getenv("SNOWFLAKE_SCHEMA"),
    "role": secrets.get("role") or os.getenv("SNOWFLAKE_ROLE")
}

required = ["user", "password", "account", "warehouse", "database", "schema"]
missing = [k for k in required if not connection_parameters.get(k)]
if missing:
    st.error(
        "Missing Snowflake credentials: {}.\nAdd them to .streamlit/secrets.toml under `[snowflake]`, set Streamlit Cloud secrets, or export corresponding environment variables (SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, ...).".format(
            ", ".join(missing)
        )
    )
    st.stop()

session = Session.builder.configs(connection_parameters).create()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).sort(col('fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    my_dataframe
    , max_selections=5
)
if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+ """')"""

    #st.write(my_insert_stmt)
    # st.stop()

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")