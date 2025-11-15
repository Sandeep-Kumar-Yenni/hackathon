-- =====================================================
-- Vendor Onboarding System - Azure SQL Database Schema
-- Based on Hackathon 2025 Problem Statement
-- =====================================================

-- Drop existing tables if they exist (for clean setup)
-- Note: Drop in reverse order of dependencies
IF OBJECT_ID('vendor_activity_logs', 'U') IS NOT NULL DROP TABLE vendor_activity_logs;
IF OBJECT_ID('vendor_followups', 'U') IS NOT NULL DROP TABLE vendor_followups;
IF OBJECT_ID('vendor_documents', 'U') IS NOT NULL DROP TABLE vendor_documents;
IF OBJECT_ID('otp_verifications', 'U') IS NOT NULL DROP TABLE otp_verifications;
IF OBJECT_ID('vendor_invitations', 'U') IS NOT NULL DROP TABLE vendor_invitations;
IF OBJECT_ID('compliance_certifications', 'U') IS NOT NULL DROP TABLE compliance_certifications;
IF OBJECT_ID('banking_information', 'U') IS NOT NULL DROP TABLE banking_information;
IF OBJECT_ID('contact_information', 'U') IS NOT NULL DROP TABLE contact_information;
IF OBJECT_ID('business_information', 'U') IS NOT NULL DROP TABLE business_information;
IF OBJECT_ID('vendor_onboarding_requests', 'U') IS NOT NULL DROP TABLE vendor_onboarding_requests;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
IF OBJECT_ID('vendor_categories', 'U') IS NOT NULL DROP TABLE vendor_categories;
IF OBJECT_ID('followup_templates', 'U') IS NOT NULL DROP TABLE followup_templates;
IF OBJECT_ID('notifications', 'U') IS NOT NULL DROP TABLE notifications;

-- =====================================================
-- Core Tables
-- =====================================================

-- Users table (for procurement team and system administrators)
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) UNIQUE NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL DEFAULT 'procurement', -- procurement, admin, reviewer
    full_name NVARCHAR(255),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Vendor Categories lookup table
CREATE TABLE vendor_categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(100) UNIQUE NOT NULL,
    description NVARCHAR(500),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Insert default vendor categories
INSERT INTO vendor_categories (category_name, description) VALUES
('IT Supplier', 'Information Technology vendors'),
('Logistics', 'Logistics and transportation vendors'),
('Office Supplies', 'Office supplies and equipment vendors'),
('Professional Services', 'Consulting and professional services'),
('Manufacturing', 'Manufacturing and production vendors'),
('Other', 'Other vendor categories');

-- Vendor Onboarding Requests table (Vendor Details Request Form)
-- This is created by procurement team to initiate vendor onboarding
CREATE TABLE vendor_onboarding_requests (
    request_id INT IDENTITY(1,1) PRIMARY KEY,
    vendor_name NVARCHAR(255) NOT NULL,
    vendor_email NVARCHAR(255) NOT NULL,
    contact_person NVARCHAR(255) NULL,
    contact_number NVARCHAR(50) NULL,
    vendor_category_id INT NULL REFERENCES vendor_categories(category_id),
    remarks NVARCHAR(1000) NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'Requested', 
    -- Status values: Requested, Waiting for vendor response, Waiting for missing data, 
    -- Waiting for validation, Validated, Denied, Deleted
    secure_link_token UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    secure_link_expires_at DATETIME2 NULL,
    email_sent_at DATETIME2 NULL,
    link_opened_at DATETIME2 NULL,
    is_deleted BIT DEFAULT 0, -- Soft delete flag
    deleted_at DATETIME2 NULL,
    deleted_by INT NULL REFERENCES users(user_id),
    created_by INT NOT NULL REFERENCES users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Business Information table (Section 1 of Vendor Onboarding Form)
CREATE TABLE business_information (
    business_info_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    legal_business_name NVARCHAR(255) NOT NULL,
    business_registration_number NVARCHAR(100) NOT NULL UNIQUE,
    business_type NVARCHAR(100) NOT NULL, -- LLC, Corporation, Partnership, etc.
    year_established INT NOT NULL, -- 1800 to current year
    business_address NVARCHAR(MAX) NOT NULL,
    number_of_employees INT NULL,
    industry_sector NVARCHAR(100) NOT NULL,
    is_completed BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    UNIQUE(request_id)
);

-- Contact Information table (Section 2 of Vendor Onboarding Form)
CREATE TABLE contact_information (
    contact_info_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    primary_contact_name NVARCHAR(255) NOT NULL,
    job_title NVARCHAR(100) NOT NULL,
    email_address NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(50) NOT NULL,
    secondary_contact_name NVARCHAR(255) NULL,
    secondary_contact_email NVARCHAR(255) NULL,
    website NVARCHAR(500) NULL,
    is_completed BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    UNIQUE(request_id)
);

-- Banking Information table (Section 3 of Vendor Onboarding Form)
CREATE TABLE banking_information (
    banking_info_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    bank_name NVARCHAR(255) NOT NULL,
    account_holder_name NVARCHAR(255) NOT NULL,
    account_number NVARCHAR(50) NOT NULL, -- 8-18 digits
    account_type NVARCHAR(50) NOT NULL, -- Checking, Savings, Business
    routing_swift_code NVARCHAR(50) NOT NULL,
    iban NVARCHAR(50) NULL,
    payment_terms NVARCHAR(100) NOT NULL,
    currency NVARCHAR(10) NOT NULL DEFAULT 'USD',
    is_completed BIT DEFAULT 0,
    is_verified BIT DEFAULT 0,
    verified_at DATETIME2 NULL,
    verified_by INT NULL REFERENCES users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    UNIQUE(request_id)
);

-- Compliance & Certifications table (Section 4 of Vendor Onboarding Form)
CREATE TABLE compliance_certifications (
    compliance_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    tax_identification_number NVARCHAR(100) NOT NULL,
    business_license_number NVARCHAR(100) NOT NULL,
    license_expiry_date DATE NOT NULL,
    insurance_provider NVARCHAR(255) NOT NULL,
    insurance_policy_number NVARCHAR(100) NOT NULL,
    insurance_expiry_date DATE NOT NULL,
    industry_certifications NVARCHAR(MAX) NULL, -- Can store multiple certifications
    is_completed BIT DEFAULT 0,
    is_verified BIT DEFAULT 0,
    verified_at DATETIME2 NULL,
    verified_by INT NULL REFERENCES users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    UNIQUE(request_id)
);

-- =====================================================
-- Authentication & Security Tables
-- =====================================================

-- OTP Verifications table (for email-based OTP authentication)
CREATE TABLE otp_verifications (
    otp_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    email NVARCHAR(255) NOT NULL,
    otp_code NVARCHAR(10) NOT NULL,
    is_used BIT DEFAULT 0,
    expires_at DATETIME2 NOT NULL,
    verified_at DATETIME2 NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Vendor Invitations table (tracks email invitations sent)
CREATE TABLE vendor_invitations (
    invitation_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    email_sent_to NVARCHAR(255) NOT NULL,
    secure_link_token UNIQUEIDENTIFIER NOT NULL,
    invitation_sent_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    link_opened_at DATETIME2 NULL,
    link_expires_at DATETIME2 NULL,
    is_expired BIT DEFAULT 0,
    sent_by INT NOT NULL REFERENCES users(user_id)
);

-- =====================================================
-- Document Management Tables
-- =====================================================

-- Vendor Documents table (for storing uploaded PDF files)
CREATE TABLE vendor_documents (
    document_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    document_type NVARCHAR(50) NOT NULL, 
    -- Values: Business, Contact-Information, Banking-Information, Compliance-Certifications
    original_filename NVARCHAR(255) NOT NULL,
    stored_filename NVARCHAR(255) NOT NULL,
    file_path NVARCHAR(MAX) NOT NULL,
    file_size BIGINT NULL, -- in bytes
    mime_type NVARCHAR(100) NULL,
    file_format NVARCHAR(10) NULL, -- pdf, docx, etc.
    upload_status NVARCHAR(50) DEFAULT 'uploaded', 
    -- Values: uploaded, processing, processed, failed
    validation_status NVARCHAR(50) DEFAULT 'pending', 
    -- Values: pending, validated, rejected
    validation_notes NVARCHAR(MAX) NULL,
    validated_at DATETIME2 NULL,
    validated_by INT NULL REFERENCES users(user_id),
    uploaded_at DATETIME2 DEFAULT GETDATE(),
    version INT DEFAULT 1,
    is_active BIT DEFAULT 1
);

-- =====================================================
-- Follow-up Management Tables
-- =====================================================

-- Follow-up Templates table (for automated follow-up messages)
CREATE TABLE followup_templates (
    template_id INT IDENTITY(1,1) PRIMARY KEY,
    template_name NVARCHAR(100) NOT NULL,
    issue_type NVARCHAR(50) NOT NULL, 
    -- Values: missing_data, incorrect_data, incorrect_file, delayed_response, pending_response
    subject NVARCHAR(255) NOT NULL,
    email_body NVARCHAR(MAX) NOT NULL,
    is_llm_generated BIT DEFAULT 0, -- Indicates if generated by LLM
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Insert default follow-up templates
INSERT INTO followup_templates (template_name, issue_type, subject, email_body) VALUES
('Missing Data', 'missing_data', 'Action Required: Complete Your Vendor Onboarding', 
 'Dear Vendor, We noticed that some required information is missing from your onboarding submission. Please complete all required fields and resubmit.'),
('Incorrect Data', 'incorrect_data', 'Action Required: Correct Information in Your Vendor Onboarding', 
 'Dear Vendor, We found some discrepancies in the information you submitted. Please review and correct the details.'),
('Incorrect File', 'incorrect_file', 'Action Required: Upload Correct Document', 
 'Dear Vendor, The document you uploaded does not match the required format or contains incorrect information. Please upload the correct document.'),
('Delayed Response', 'delayed_response', 'Reminder: Complete Your Vendor Onboarding', 
 'Dear Vendor, This is a reminder to complete your vendor onboarding process. Please submit your information at your earliest convenience.'),
('Pending Response', 'pending_response', 'Follow-up: Vendor Onboarding Status', 
 'Dear Vendor, We are following up on your vendor onboarding request. Please respond to our previous communication.');

-- Vendor Follow-ups table (tracks all follow-up communications)
CREATE TABLE vendor_followups (
    followup_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    followup_type NVARCHAR(50) NOT NULL, 
    -- Values: missing_data, incorrect_data, incorrect_file, delayed_response, pending_response, manual
    issue_description NVARCHAR(MAX) NULL,
    template_id INT NULL REFERENCES followup_templates(template_id),
    email_subject NVARCHAR(255) NOT NULL,
    email_body NVARCHAR(MAX) NOT NULL,
    is_llm_generated BIT DEFAULT 0, -- Indicates if generated by LLM
    is_automated BIT DEFAULT 0, -- Indicates if triggered automatically
    sent_at DATETIME2 NULL,
    response_received_at DATETIME2 NULL,
    status NVARCHAR(50) DEFAULT 'pending', -- pending, sent, responded, resolved
    created_by INT NOT NULL REFERENCES users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    next_followup_date DATETIME2 NULL,
    followup_count INT DEFAULT 1 -- Track number of follow-ups for same issue
);

-- =====================================================
-- Activity Logging & Notifications Tables
-- =====================================================

-- Vendor Activity Logs table (timeline of all actions and communications)
CREATE TABLE vendor_activity_logs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL REFERENCES vendor_onboarding_requests(request_id) ON DELETE CASCADE,
    activity_type NVARCHAR(50) NOT NULL, 
    -- Values: request_created, email_sent, link_opened, form_submitted, document_uploaded, 
    -- status_changed, followup_sent, validation_completed, etc.
    activity_description NVARCHAR(MAX) NOT NULL,
    performed_by INT NULL REFERENCES users(user_id), -- NULL if system-generated
    performed_by_vendor BIT DEFAULT 0, -- Indicates if action was by vendor
    metadata NVARCHAR(MAX) NULL, -- JSON string for additional details
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Notifications table (in-app notifications for procurement team)
CREATE TABLE notifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    request_id INT NULL REFERENCES vendor_onboarding_requests(request_id),
    notification_type NVARCHAR(50) NOT NULL,
    -- Values: vendor_response, status_change, followup_required, validation_complete, etc.
    title NVARCHAR(255) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    is_read BIT DEFAULT 0,
    read_at DATETIME2 NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Vendor Onboarding Requests indexes
CREATE INDEX idx_vendor_requests_status ON vendor_onboarding_requests(status);
CREATE INDEX idx_vendor_requests_email ON vendor_onboarding_requests(vendor_email);
CREATE INDEX idx_vendor_requests_token ON vendor_onboarding_requests(secure_link_token);
CREATE INDEX idx_vendor_requests_category ON vendor_onboarding_requests(vendor_category_id);
CREATE INDEX idx_vendor_requests_deleted ON vendor_onboarding_requests(is_deleted);
CREATE INDEX idx_vendor_requests_created_at ON vendor_onboarding_requests(created_at);

-- Business Information indexes
CREATE INDEX idx_business_request_id ON business_information(request_id);
CREATE INDEX idx_business_reg_number ON business_information(business_registration_number);

-- Contact Information indexes
CREATE INDEX idx_contact_request_id ON contact_information(request_id);
CREATE INDEX idx_contact_email ON contact_information(email_address);

-- Banking Information indexes
CREATE INDEX idx_banking_request_id ON banking_information(request_id);

-- Compliance indexes
CREATE INDEX idx_compliance_request_id ON compliance_certifications(request_id);
CREATE INDEX idx_compliance_tax_id ON compliance_certifications(tax_identification_number);
CREATE INDEX idx_compliance_license_expiry ON compliance_certifications(license_expiry_date);
CREATE INDEX idx_compliance_insurance_expiry ON compliance_certifications(insurance_expiry_date);

-- Document indexes
CREATE INDEX idx_documents_request_id ON vendor_documents(request_id);
CREATE INDEX idx_documents_type ON vendor_documents(document_type);
CREATE INDEX idx_documents_status ON vendor_documents(validation_status);

-- OTP indexes
CREATE INDEX idx_otp_request_id ON otp_verifications(request_id);
CREATE INDEX idx_otp_email ON otp_verifications(email);
CREATE INDEX idx_otp_expires ON otp_verifications(expires_at);

-- Follow-up indexes
CREATE INDEX idx_followups_request_id ON vendor_followups(request_id);
CREATE INDEX idx_followups_status ON vendor_followups(status);
CREATE INDEX idx_followups_type ON vendor_followups(followup_type);
CREATE INDEX idx_followups_next_date ON vendor_followups(next_followup_date);

-- Activity Log indexes
CREATE INDEX idx_activity_request_id ON vendor_activity_logs(request_id);
CREATE INDEX idx_activity_type ON vendor_activity_logs(activity_type);
CREATE INDEX idx_activity_created_at ON vendor_activity_logs(created_at);

-- Notification indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_request_id ON notifications(request_id);

-- =====================================================
-- Triggers for Updated At Timestamps
-- =====================================================

-- Trigger for updating updated_at timestamp on vendor_onboarding_requests
CREATE TRIGGER trg_vendor_requests_updated_at
ON vendor_onboarding_requests
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE vendor_onboarding_requests
    SET updated_at = GETDATE()
    FROM vendor_onboarding_requests v
    INNER JOIN inserted i ON v.request_id = i.request_id;
END;

-- Trigger for updating updated_at timestamp on business_information
CREATE TRIGGER trg_business_info_updated_at
ON business_information
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE business_information
    SET updated_at = GETDATE()
    FROM business_information b
    INNER JOIN inserted i ON b.business_info_id = i.business_info_id;
END;

-- Trigger for updating updated_at timestamp on contact_information
CREATE TRIGGER trg_contact_info_updated_at
ON contact_information
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE contact_information
    SET updated_at = GETDATE()
    FROM contact_information c
    INNER JOIN inserted i ON c.contact_info_id = i.contact_info_id;
END;

-- Trigger for updating updated_at timestamp on banking_information
CREATE TRIGGER trg_banking_info_updated_at
ON banking_information
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE banking_information
    SET updated_at = GETDATE()
    FROM banking_information b
    INNER JOIN inserted i ON b.banking_info_id = i.banking_info_id;
END;

-- Trigger for updating updated_at timestamp on compliance_certifications
CREATE TRIGGER trg_compliance_updated_at
ON compliance_certifications
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE compliance_certifications
    SET updated_at = GETDATE()
    FROM compliance_certifications c
    INNER JOIN inserted i ON c.compliance_id = i.compliance_id;
END;

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- View for Vendor Dashboard (comprehensive vendor list with all details)
CREATE VIEW vw_vendor_dashboard AS
SELECT 
    v.request_id,
    v.vendor_name,
    v.vendor_email,
    v.contact_person,
    v.contact_number,
    vc.category_name AS vendor_category,
    v.status,
    v.secure_link_token,
    v.email_sent_at,
    v.link_opened_at,
    v.created_at,
    v.updated_at,
    v.is_deleted,
    v.deleted_at,
    u.username AS created_by_username,
    -- Business Information
    b.legal_business_name,
    b.business_registration_number,
    b.business_type,
    b.is_completed AS business_completed,
    -- Contact Information
    c.primary_contact_name,
    c.email_address AS contact_email,
    c.is_completed AS contact_completed,
    -- Banking Information
    bk.bank_name,
    bk.is_completed AS banking_completed,
    -- Compliance
    comp.tax_identification_number,
    comp.is_completed AS compliance_completed,
    -- Document counts
    (SELECT COUNT(*) FROM vendor_documents WHERE request_id = v.request_id AND is_active = 1) AS document_count,
    -- Follow-up counts
    (SELECT COUNT(*) FROM vendor_followups WHERE request_id = v.request_id AND status = 'pending') AS pending_followups,
    -- Last activity
    (SELECT TOP 1 created_at FROM vendor_activity_logs WHERE request_id = v.request_id ORDER BY created_at DESC) AS last_activity_at
FROM vendor_onboarding_requests v
LEFT JOIN vendor_categories vc ON v.vendor_category_id = vc.category_id
LEFT JOIN users u ON v.created_by = u.user_id
LEFT JOIN business_information b ON v.request_id = b.request_id
LEFT JOIN contact_information c ON v.request_id = c.request_id
LEFT JOIN banking_information bk ON v.request_id = bk.request_id
LEFT JOIN compliance_certifications comp ON v.request_id = comp.request_id;

-- View for Dashboard Metrics
CREATE VIEW vw_dashboard_metrics AS
SELECT 
    COUNT(*) AS total_vendors,
    SUM(CASE WHEN status = 'Requested' THEN 1 ELSE 0 END) AS requested_count,
    SUM(CASE WHEN status = 'Waiting for vendor response' THEN 1 ELSE 0 END) AS waiting_response_count,
    SUM(CASE WHEN status = 'Waiting for missing data' THEN 1 ELSE 0 END) AS waiting_missing_data_count,
    SUM(CASE WHEN status = 'Waiting for validation' THEN 1 ELSE 0 END) AS waiting_validation_count,
    SUM(CASE WHEN status = 'Validated' THEN 1 ELSE 0 END) AS validated_count,
    SUM(CASE WHEN status = 'Denied' THEN 1 ELSE 0 END) AS denied_count,
    SUM(CASE WHEN is_deleted = 1 THEN 1 ELSE 0 END) AS deleted_count,
    (SELECT COUNT(*) FROM vendor_followups WHERE status = 'pending') AS pending_followups_count,
    (SELECT AVG(DATEDIFF(HOUR, created_at, link_opened_at)) 
     FROM vendor_onboarding_requests 
     WHERE link_opened_at IS NOT NULL) AS avg_response_time_hours
FROM vendor_onboarding_requests
WHERE is_deleted = 0;

-- =====================================================
-- Stored Procedures (Optional - for common operations)
-- =====================================================

-- Stored Procedure: Get vendor details with all related information
CREATE PROCEDURE sp_get_vendor_details
    @request_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT * FROM vendor_onboarding_requests WHERE request_id = @request_id;
    SELECT * FROM business_information WHERE request_id = @request_id;
    SELECT * FROM contact_information WHERE request_id = @request_id;
    SELECT * FROM banking_information WHERE request_id = @request_id;
    SELECT * FROM compliance_certifications WHERE request_id = @request_id;
    SELECT * FROM vendor_documents WHERE request_id = @request_id AND is_active = 1;
    SELECT * FROM vendor_followups WHERE request_id = @request_id ORDER BY created_at DESC;
    SELECT * FROM vendor_activity_logs WHERE request_id = @request_id ORDER BY created_at DESC;
END;

-- =====================================================
-- End of Schema
-- =====================================================

-- Sample data insertion (commented out - uncomment for testing)
/*
-- Insert a default admin user (password should be hashed in production)
INSERT INTO users (username, email, password_hash, role, full_name) 
VALUES ('admin', 'admin@example.com', 'hashed_password_here', 'admin', 'System Administrator');

-- Insert a procurement user
INSERT INTO users (username, email, password_hash, role, full_name) 
VALUES ('procurement1', 'procurement@example.com', 'hashed_password_here', 'procurement', 'Procurement User');
*/