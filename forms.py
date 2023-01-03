from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class GetNamespace(FlaskForm):
    pod_namespace = StringField('NamespaceName',validators=[DataRequired(), Length(min=3, max=20)])
    user_name = StringField('UserName', validators=[DataRequired()])
    submit = SubmitField('Submit')

class GetParameter(FlaskForm):
    parameter_name = StringField('Parameter Key',validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Submit')



class UpdateParameter(FlaskForm):
    parameter_name = StringField('Parameter Key',validators=[DataRequired()])
    parameter_key = StringField('Parameter Value', validators=[DataRequired()])
    submit = SubmitField('Submit')
