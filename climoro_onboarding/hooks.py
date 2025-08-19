app_name = "climoro_onboarding"
app_title = "Climoro Onboarding"
app_publisher = "climoro"
app_description = "Multi-step onboarding form for Climoro"
app_email = "info.climoro@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "climoro_onboarding",
# 		"logo": "/assets/climoro_onboarding/logo.png",
# 		"title": "Climoro Onboarding",
# 		"route": "/climoro_onboarding",
# 		"has_permission": "climoro_onboarding.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/climoro_onboarding/css/climoro_onboarding.css"
# app_include_js = "/assets/climoro_onboarding/js/climoro_onboarding.js"

# include js, css files in header of web template
# web_include_css = "/assets/climoro_onboarding/css/climoro_onboarding.css"
# web_include_js = "/assets/climoro_onboarding/js/climoro_onboarding.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "climoro_onboarding/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Onboarding Form": "climoro_onboarding/doctype/onboarding_form/onboarding_form.js"
}
# add list view js for buttons/actions
doctype_list_js = {
    "GHG Report": "climoro_onboarding/doctype/ghg_report/ghg_report_list.js"
}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "climoro_onboarding/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "climoro_onboarding.utils.jinja_methods",
# 	"filters": "climoro_onboarding.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "climoro_onboarding.install.before_install"
# after_install = "climoro_onboarding.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "climoro_onboarding.uninstall.before_uninstall"
# after_uninstall = "climoro_onboarding.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "climoro_onboarding.utils.before_app_install"
# after_app_install = "climoro_onboarding.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "climoro_onboarding.utils.before_app_uninstall"
# after_app_uninstall = "climoro_onboarding.utils.after_app_uninstall"

# Auto-migrate on startup
# ----------
# auto_migrate = True

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "climoro_onboarding.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"climoro_onboarding.tasks.all"
# 	],
# 	"daily": [
# 		"climoro_onboarding.tasks.daily"
# 	],
# 	"hourly": [
# 		"climoro_onboarding.tasks.hourly"
# 	],
# 	"weekly": [
# 		"climoro_onboarding.tasks.weekly"
# 	],
# 	"monthly": [
# 		"climoro_onboarding.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "climoro_onboarding.install.before_tests"

# Whitelisted Methods
# -------------------
# Methods that can be called from client-side
whitelisted_methods = [
    "climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.send_admin_notification",
    "climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.get_google_maps_api_key",
    "climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.get_sub_industry_options",
    "climoro_onboarding.www.apply.api.submit_onboarding_form",
    "climoro_onboarding.www.apply.api.get_existing_application",
    "climoro_onboarding.www.apply.api.save_step_data",
    "climoro_onboarding.www.apply.api.send_verification_email",
    "climoro_onboarding.www.apply.api.verify_email",
    "climoro_onboarding.www.apply.api.get_session_data",
    "climoro_onboarding.www.apply.api.test_email_verification_flow"
]

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "climoro_onboarding.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "climoro_onboarding.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["climoro_onboarding.utils.before_request"]
# after_request = ["climoro_onboarding.utils.after_request"]

# Job Events
# ----------
# before_job = ["climoro_onboarding.utils.before_job"]
# after_job = ["climoro_onboarding.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"climoro_onboarding.auth.validate"
# ]

# Automatically update python controller files with type annotations for Frappe 15+
# tsconfigjson_template = "climoro_onboarding/public/build.json"

# Fixtures
# --------
fixtures = ["Onboarding Form", "Dashboard Chart", "Number Card"]

# Dashboard overrides
override_doctype_dashboards = {
    "Stationary Emissions": "climoro_onboarding.dashboard.get_stationary_emissions_dashboard",
    "Electricity Purchased": "climoro_onboarding.dashboard.get_electricity_dashboard",
    "Downstream Transportation Method": "climoro_onboarding.dashboard.get_transportation_dashboard"
}

