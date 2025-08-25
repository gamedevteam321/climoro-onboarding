// GHG Reports Viewer JavaScript

class GHGReportsViewer {
    constructor() {
        this.currentUser = null;
        this.currentCompany = null;
        this.isAdmin = false;
        this.reports = [];
        this.companies = [];
        this.filters = {
            company: '',
            dateFrom: '',
            dateTo: ''
        };
        
        this.init();
    }

    async init() {
        try {
            await this.loadUserInfo();
            await this.loadCompanies();
            this.setupEventListeners();
            await this.loadReports();
            this.updateUI();
        } catch (error) {
            console.error('Initialization error:', error);
            this.showMessage('Error initializing viewer', 'error');
        }
    }

    async loadUserInfo() {
        try {
            const response = await this.makeRequest('frappe.client.get_value', {
                doctype: 'User',
                filters: { name: frappe.session.user },
                fieldname: ['name', 'full_name', 'company']
            });

            if (response.message) {
                this.currentUser = response.message;
                this.currentCompany = this.currentUser.company;
                
                // Check if user is admin
                const hasRole = await this.makeRequest('frappe.has_permission', {
                    doctype: 'GHG Report',
                    ptype: 'read',
                    user: frappe.session.user
                });
                
                this.isAdmin = hasRole.message;
            }
        } catch (error) {
            console.error('Error loading user info:', error);
        }
    }

    async loadCompanies() {
        try {
            const response = await this.makeRequest('frappe.client.get_list', {
                doctype: 'Company',
                fields: ['name', 'company_name'],
                limit: 10
            });

            if (response.message) {
                this.companies = response.message;
                this.populateCompanyFilters();
            }
        } catch (error) {
            console.error('Error loading companies:', error);
        }
    }

    async loadReports() {
        try {
            this.showLoading(true);
            
            // Build filters based on user permissions
            let filters = {};
            
            if (!this.isAdmin && this.currentCompany) {
                filters.organization_name = this.currentCompany;
            }
            
            if (this.filters.company) {
                filters.organization_name = this.filters.company;
            }
            
            if (this.filters.dateFrom) {
                filters.period_from = ['>=', this.filters.dateFrom];
            }
            
            if (this.filters.dateTo) {
                filters.period_to = ['<=', this.filters.dateTo];
            }

            const response = await this.makeRequest('frappe.client.get_list', {
                doctype: 'GHG Report',
                fields: [
                    'name', 'report_title', 'organization_name', 'period_from', 
                    'period_to', 'docstatus', 'creation', 'modified'
                ],
                filters: filters,
                limit: 1000,
                order_by: 'creation desc'
            });

            if (response.message) {
                this.reports = response.message;
                this.renderReportsTable();
            }
        } catch (error) {
            console.error('Error loading reports:', error);
            this.showMessage('Error loading reports', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    populateCompanyFilters() {
        const companyFilter = document.getElementById('company-filter');
        const modalCompany = document.getElementById('modal-company');
        
        // Clear existing options
        companyFilter.innerHTML = '<option value="">All Companies</option>';
        modalCompany.innerHTML = '<option value="">Select Company</option>';
        
        // Add company options
        this.companies.forEach(company => {
            const option1 = document.createElement('option');
            option1.value = company.name;
            option1.textContent = company.company_name || company.name;
            companyFilter.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = company.name;
            option2.textContent = company.company_name || company.name;
            modalCompany.appendChild(option2);
        });
        
        // Set default company for non-admin users
        if (!this.isAdmin && this.currentCompany) {
            companyFilter.value = this.currentCompany;
            modalCompany.value = this.currentCompany;
            this.filters.company = this.currentCompany;
        }
    }

    renderReportsTable() {
        const tbody = document.getElementById('reports-tbody');
        const noReports = document.getElementById('no-reports');
        
        if (this.reports.length === 0) {
            tbody.innerHTML = '';
            noReports.classList.remove('hidden');
            return;
        }
        
        noReports.classList.add('hidden');
        
        tbody.innerHTML = this.reports.map(report => `
            <tr>
                <td>
                    <strong>${this.escapeHtml(report.report_title || 'Untitled')}</strong>
                    <br><small class="text-muted">${report.name}</small>
                </td>
                <td>${this.escapeHtml(report.organization_name || 'N/A')}</td>
                <td>${report.period_from ? this.formatDate(report.period_from) : 'N/A'}</td>
                <td>${report.period_to ? this.formatDate(report.period_to) : 'N/A'}</td>
                <td>
                    <span class="status-badge status-${this.getStatusClass(report.docstatus)}">
                        ${this.getStatusText(report.docstatus)}
                    </span>
                </td>
                <td>${this.formatDate(report.creation)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="ghgViewer.viewReport('${report.name}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-success" onclick="ghgViewer.generatePDF('${report.name}')">
                            <i class="fas fa-file-pdf"></i> PDF
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getStatusClass(docstatus) {
        switch (docstatus) {
            case 0: return 'draft';
            case 1: return 'submitted';
            case 2: return 'approved';
            default: return 'draft';
        }
    }

    getStatusText(docstatus) {
        switch (docstatus) {
            case 0: return 'Draft';
            case 1: return 'Submitted';
            case 2: return 'Approved';
            default: return 'Draft';
        }
    }

    async generatePDF(reportName) {
        try {
            this.showLoadingOverlay(true);
            
            const response = await this.makeRequest('climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.generate_ghg_report_pdf', {
                doctype: 'GHG Report',
                name: reportName
            });

            if (response.message && response.message.success) {
                this.showMessage('PDF generated successfully!', 'success');
                
                // Download the PDF
                if (response.message.file_url) {
                    const link = document.createElement('a');
                    link.href = response.message.file_url;
                    link.download = response.message.file_name || 'GHG_Report.pdf';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            } else {
                this.showMessage(response.message?.message || 'Error generating PDF', 'error');
            }
        } catch (error) {
            console.error('Error generating PDF:', error);
            this.showMessage('Error generating PDF', 'error');
        } finally {
            this.showLoadingOverlay(false);
        }
    }

    async createAndGenerateReport(formData) {
        try {
            this.showLoadingOverlay(true);
            
            // Create new GHG Report
            const reportData = {
                doctype: 'GHG Report',
                report_title: formData.reportTitle,
                organization_name: formData.company,
                period_from: formData.periodFrom,
                period_to: formData.periodTo
            };

            const createResponse = await this.makeRequest('frappe.client.insert', {
                doc: reportData
            });

            if (createResponse.message) {
                const reportName = createResponse.message.name;
                
                // Generate PDF for the new report
                const pdfResponse = await this.makeRequest('climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.generate_ghg_report_pdf', {
                    doctype: 'GHG Report',
                    name: reportName
                });

                if (pdfResponse.message && pdfResponse.message.success) {
                    this.showMessage('Report created and PDF generated successfully!', 'success');
                    
                    // Download the PDF
                    if (pdfResponse.message.file_url) {
                        const link = document.createElement('a');
                        link.href = pdfResponse.message.file_url;
                        link.download = pdfResponse.message.file_name || 'GHG_Report.pdf';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }
                    
                    // Refresh reports list
                    await this.loadReports();
                    this.closeModal();
                } else {
                    this.showMessage('Report created but PDF generation failed', 'error');
                }
            } else {
                this.showMessage('Error creating report', 'error');
            }
        } catch (error) {
            console.error('Error creating and generating report:', error);
            this.showMessage('Error creating report', 'error');
        } finally {
            this.showLoadingOverlay(false);
        }
    }

    viewReport(reportName) {
        // Open the report in Frappe Desk
        frappe.set_route('Form', 'GHG Report', reportName);
    }

    setupEventListeners() {
        // Filter events
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });

        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });

        document.getElementById('refresh-reports').addEventListener('click', () => {
            this.loadReports();
        });

        document.getElementById('generate-new-report').addEventListener('click', () => {
            this.openModal();
        });

        // Modal events
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('cancel-generate').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('submit-generate').addEventListener('click', (e) => {
            e.preventDefault();
            this.submitGenerateForm();
        });

        // Close modal on outside click
        document.getElementById('generate-modal').addEventListener('click', (e) => {
            if (e.target.id === 'generate-modal') {
                this.closeModal();
            }
        });

        // Form submission
        document.getElementById('generate-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitGenerateForm();
        });
    }

    applyFilters() {
        this.filters.company = document.getElementById('company-filter').value;
        this.filters.dateFrom = document.getElementById('date-from').value;
        this.filters.dateTo = document.getElementById('date-to').value;
        
        this.loadReports();
    }

    clearFilters() {
        document.getElementById('company-filter').value = '';
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        
        this.filters = {
            company: '',
            dateFrom: '',
            dateTo: ''
        };
        
        this.loadReports();
    }

    openModal() {
        const modal = document.getElementById('generate-modal');
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Set default dates
        const today = new Date();
        const yearStart = new Date(today.getFullYear(), 0, 1);
        const yearEnd = new Date(today.getFullYear(), 11, 31);
        
        document.getElementById('modal-period-from').value = this.formatDateForInput(yearStart);
        document.getElementById('modal-period-to').value = this.formatDateForInput(yearEnd);
        
        // Set default company for non-admin users
        if (!this.isAdmin && this.currentCompany) {
            document.getElementById('modal-company').value = this.currentCompany;
        }
    }

    closeModal() {
        const modal = document.getElementById('generate-modal');
        modal.classList.remove('show');
        setTimeout(() => modal.classList.add('hidden'), 300);
        
        // Reset form
        document.getElementById('generate-form').reset();
    }

    submitGenerateForm() {
        const form = document.getElementById('generate-form');
        const formData = new FormData(form);
        
        const data = {
            company: formData.get('modal-company') || document.getElementById('modal-company').value,
            periodFrom: formData.get('modal-period-from') || document.getElementById('modal-period-from').value,
            periodTo: formData.get('modal-period-to') || document.getElementById('modal-period-to').value,
            reportTitle: formData.get('modal-report-title') || document.getElementById('modal-report-title').value
        };
        
        // Validate form
        if (!data.company || !data.periodFrom || !data.periodTo || !data.reportTitle) {
            this.showMessage('Please fill in all required fields', 'error');
            return;
        }
        
        if (new Date(data.periodFrom) > new Date(data.periodTo)) {
            this.showMessage('Start date must be before end date', 'error');
            return;
        }
        
        this.createAndGenerateReport(data);
    }

    updateUI() {
        // Update user info display
        if (this.currentUser) {
            document.getElementById('user-name').textContent = this.currentUser.full_name || this.currentUser.name;
            document.getElementById('user-company').textContent = this.currentCompany || 'No Company';
        }
        
        // Update company filter visibility for non-admin users
        if (!this.isAdmin && this.currentCompany) {
            const companyFilter = document.getElementById('company-filter');
            companyFilter.disabled = true;
            companyFilter.title = 'Company filter is disabled for your role';
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const table = document.getElementById('reports-table');
        
        if (show) {
            loading.classList.remove('hidden');
            table.style.opacity = '0.5';
        } else {
            loading.classList.add('hidden');
            table.style.opacity = '1';
        }
    }

    showLoadingOverlay(show) {
        const overlay = document.getElementById('loading-overlay');
        
        if (show) {
            overlay.classList.remove('hidden');
            setTimeout(() => overlay.classList.add('show'), 10);
        } else {
            overlay.classList.remove('show');
            setTimeout(() => overlay.classList.add('hidden'), 300);
        }
    }

    showMessage(message, type = 'info') {
        const container = document.getElementById('message-container');
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = message;
        
        container.appendChild(messageEl);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 5000);
    }

    async makeRequest(method, args) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: method,
                args: args,
                callback: resolve,
                error: reject
            });
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }
}

// Initialize the viewer when the page loads
let ghgViewer;
document.addEventListener('DOMContentLoaded', () => {
    ghgViewer = new GHGReportsViewer();
});

// Global functions for onclick handlers
window.ghgViewer = null;
document.addEventListener('DOMContentLoaded', () => {
    window.ghgViewer = ghgViewer;
});
