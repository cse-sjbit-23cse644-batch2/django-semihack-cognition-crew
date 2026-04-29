from django import forms
from django.db.models import Q
from .models import Domain, Project, TeamMember, Phase, Submission, Feedback, Evaluation
from auth_app.models import User


class DomainForm(forms.ModelForm):
    """Form for creating and updating domains"""

    class Meta:
        model = Domain
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects"""

    new_domain_name = forms.CharField(
        label='New Domain',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Example: Artificial Intelligence'
        }),
        help_text='Use this only when the domain is not already listed.'
    )
    new_domain_description = forms.CharField(
        label='Domain Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional short description for the new domain'
        })
    )

    class Meta:
        model = Project
        fields = ['title', 'domain', 'guide', 'coordinator']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter project title', 'class': 'form-control'}),
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'guide': forms.Select(attrs={'class': 'form-select'}),
            'coordinator': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show guides as potential project guides
        self.fields['guide'].queryset = User.objects.filter(role='GUIDE')
        self.fields['coordinator'].queryset = User.objects.filter(role='COORDINATOR')
        self.fields['domain'].queryset = Domain.objects.all().order_by('name')
        self.fields['domain'].required = False
        self.fields['domain'].empty_label = "Select existing domain"

        # Role-based field visibility
        if self.user and self.user.role == 'STUDENT':
            # Students can't assign guides or coordinators
            self.fields.pop('guide', None)
            self.fields.pop('coordinator', None)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                    field.widget.attrs['class'] = 'form-select'
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        domain = cleaned_data.get('domain')
        new_domain_name = (cleaned_data.get('new_domain_name') or '').strip()

        if not domain and not new_domain_name:
            raise forms.ValidationError('Choose an existing domain or enter a new domain name.')

        if new_domain_name:
            existing_domain = Domain.objects.filter(name__iexact=new_domain_name).first()
            if existing_domain:
                cleaned_data['domain'] = existing_domain

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_domain_name = (self.cleaned_data.get('new_domain_name') or '').strip()

        if new_domain_name and not self.cleaned_data.get('domain'):
            domain = Domain(
                name=new_domain_name,
                description=self.cleaned_data.get('new_domain_description') or '',
                created_by=self.user if self.user and self.user.is_authenticated else None
            )
            domain.full_clean()
            if commit:
                domain.save()
            instance.domain = domain
        elif self.cleaned_data.get('domain'):
            instance.domain = self.cleaned_data['domain']

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class TeamMemberForm(forms.ModelForm):
    """Form for adding team members to projects"""

    class Meta:
        model = TeamMember
        fields = ['user', 'project', 'role']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            existing_students = TeamMember.objects.filter(project=project).values_list('user', flat=True)
            busy_students = TeamMember.objects.filter(
                project__status='ACTIVE'
            ).exclude(project=project).values_list('user', flat=True)
            available_students = User.objects.filter(role='STUDENT').exclude(
                id__in=existing_students
            ).exclude(id__in=busy_students)
            self.fields['user'].queryset = available_students
            self.fields['project'].initial = project
            self.fields['project'].widget = forms.HiddenInput()


class PhaseForm(forms.ModelForm):
    """Form for creating and updating phases"""

    class Meta:
        model = Phase
        fields = ['name', 'description', 'order', 'deadline_offset_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SubmissionForm(forms.ModelForm):
    """Form for creating submissions"""

    class Meta:
        model = Submission
        fields = ['phase']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if project:
            self.instance.project = project
            # Only show phases that the project can access
            accessible_phases = []
            for phase in Phase.objects.all():
                if project.can_access_phase(phase):
                    accessible_phases.append(phase.pk)

            self.fields['phase'].queryset = Phase.objects.filter(
                pk__in=accessible_phases
            )


class VersionUploadForm(forms.Form):
    """Form for uploading new versions of submissions"""

    file = forms.FileField(
        label='Upload File',
        help_text='Supported formats: PDF, DOC, DOCX, ZIP, TXT (Max 10MB)',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    change_summary = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text='Describe the changes made in this version'
    )

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Ensure form control classes
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB')

            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.zip', '.txt']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    f'File type not supported. Allowed: {", ".join(allowed_extensions)}'
                )

        return file


class FeedbackForm(forms.ModelForm):
    """Form for creating feedback on submissions"""

    class Meta:
        model = Feedback
        fields = ['submission', 'version', 'comment', 'resolved']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'submission': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.Select(attrs={'class': 'form-select'}),
            'resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.submission_instance = kwargs.pop('submission', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.role == 'GUIDE':
                self.fields['submission'].queryset = Submission.objects.filter(
                    project__guide=self.user
                ).select_related('project', 'phase')
            elif self.user.role == 'ADMIN':
                self.fields['submission'].queryset = Submission.objects.all().select_related('project', 'phase')

        if self.submission_instance is not None:
            self.fields['submission'].initial = self.submission_instance.pk
            self.fields['submission'].widget = forms.HiddenInput()
            self.fields['version'].queryset = Version.objects.filter(submission=self.submission_instance).order_by('-version_number')
        else:
            submission_id = self.initial.get('submission') or self.data.get('submission')
            if submission_id:
                self.fields['version'].queryset = Version.objects.filter(submission_id=submission_id).order_by('-version_number')
            else:
                self.fields['version'].queryset = Version.objects.all().order_by('-submission', '-version_number')


    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.given_by = self.user
        if self.submission_instance is not None:
            instance.submission = self.submission_instance
        if commit:
            instance.save()
        return instance


class BulkStudentImportForm(forms.Form):
    """Form for bulk importing students"""

    csv_file = forms.FileField(
        label='CSV File',
        help_text='CSV format: username,email,first_name,last_name,domain_name'
    )

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file:
            # Check file extension
            if not file.name.lower().endswith('.csv'):
                raise forms.ValidationError('File must be a CSV file')

            # Check file size (1MB limit)
            if file.size > 1024 * 1024:
                raise forms.ValidationError('File size must be under 1MB')

        return file


class ProjectSearchForm(forms.Form):
    """Form for searching and filtering projects"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search projects...'})
    )
    domain = forms.ModelChoiceField(
        queryset=Domain.objects.all(),
        required=False,
        empty_label="All Domains"
    )
    guide = forms.ModelChoiceField(
        queryset=User.objects.filter(role='GUIDE'),
        required=False,
        empty_label="All Guides"
    )
    coordinator = forms.ModelChoiceField(
        queryset=User.objects.filter(role='COORDINATOR'),
        required=False,
        empty_label="All Coordinators"
    )
    publication_status = forms.ChoiceField(
        choices=[('', 'All')] + list(Project.PUBLICATION_CHOICES),
        required=False,
        widget=forms.Select()
    )


class StudentForm(forms.ModelForm):
    """Form for creating and updating students"""

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Required for new users. Leave blank while editing to keep the current password.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Unique username for the student"
        self.fields['email'].help_text = "Student's email address"
        if not self.instance.pk:
            self.fields['password'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = 'STUDENT'
        password = self.cleaned_data.get('password')
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


class GuideForm(forms.ModelForm):
    """Form for creating and updating guides"""

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Required for new users. Leave blank while editing to keep the current password.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        if not self.instance.pk:
            self.fields['password'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = 'GUIDE'
        password = self.cleaned_data.get('password')
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


class CoordinatorForm(forms.ModelForm):
    """Form for creating and updating coordinators"""

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Required for new users. Leave blank while editing to keep the current password.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        if not self.instance.pk:
            self.fields['password'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = 'COORDINATOR'
        password = self.cleaned_data.get('password')
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


class GuideAllotmentForm(forms.Form):
    """Form for assigning a project to a guide, coordinator, and student team."""

    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        empty_label="Select Project",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    guide = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select Guide",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    coordinator = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Select Coordinator",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select one or more students for this project. The first selected student becomes team leader."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.select_related('domain').order_by('title')
        self.fields['guide'].queryset = User.objects.filter(role='GUIDE').order_by('first_name', 'username')
        self.fields['coordinator'].queryset = User.objects.filter(role='COORDINATOR').order_by('first_name', 'username')
        self.fields['students'].queryset = User.objects.filter(role='STUDENT').order_by('first_name', 'username')

        project = None
        project_id = self.data.get('project') if self.is_bound else self.initial.get('project')
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except (Project.DoesNotExist, ValueError, TypeError):
                project = None

        if project:
            current_student_ids = project.team_members.values_list('user_id', flat=True)
            self.fields['students'].queryset = User.objects.filter(role='STUDENT').filter(
                Q(project_memberships__project__status='ACTIVE', project_memberships__project=project) |
                Q(project_memberships__isnull=True) |
                Q(project_memberships__project__status__in=['COMPLETED', 'ARCHIVED', 'SUSPENDED'])
            ).distinct().order_by('first_name', 'username')
            self.fields['guide'].initial = project.guide_id
            self.fields['coordinator'].initial = project.coordinator_id
            self.fields['students'].initial = list(current_student_ids)

    def clean_students(self):
        students = self.cleaned_data['students']
        project = self.cleaned_data.get('project')
        if not project:
            return students

        unavailable = []
        for student in students:
            other_active_project = TeamMember.objects.filter(
                user=student,
                project__status='ACTIVE'
            ).exclude(project=project).select_related('project').first()
            if other_active_project:
                unavailable.append(f"{student.get_full_name() or student.username} ({other_active_project.project.title})")

        if unavailable:
            raise forms.ValidationError(
                "These students are already assigned to another active project: " + ", ".join(unavailable)
            )

        return students


class EvaluationForm(forms.ModelForm):
    """Form for creating evaluations"""

    class Meta:
        model = Evaluation
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.RadioSelect(choices=Evaluation.RATING_CHOICES, attrs={'class': 'form-check-input'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.phase = kwargs.pop('phase', None)
        self.evaluator = kwargs.pop('evaluator', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.project = self.project
        instance.phase = self.phase
        instance.evaluator = self.evaluator
        if commit:
            instance.save()
        return instance


class CertificateUploadForm(forms.ModelForm):
    """Form for uploading certificates"""

    class Meta:
        model = Project
        fields = ['certificate']
        widgets = {
            'certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        }
    status = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('planning', 'Planning'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold'),
        ],
        required=False
    )
