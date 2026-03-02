from pydantic import BaseModel, Field
from typing import List, Optional


# =========================
# COMMON CONFIG
# =========================

class StrictBaseModel(BaseModel):
    model_config = {
        "extra": "allow"  # keys cannot change
    }


# =========================
# RESUME SCHEMA
# =========================

class Candidate(StrictBaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None


class EducationEntry(StrictBaseModel):
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceEntry(StrictBaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)


class Skills(StrictBaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class Certification(StrictBaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None


class Project(StrictBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class ResumeSchema(StrictBaseModel):
    candidate: Candidate = Field(default_factory=Candidate)
    summary: Optional[str] = None
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)


# =========================
# INVOICE SCHEMA
# =========================

class InvoiceDetails(StrictBaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    purchase_order_number: Optional[str] = None
    currency: Optional[str] = None


class Vendor(StrictBaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None


class BillTo(StrictBaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class LineItem(StrictBaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class Amounts(StrictBaseModel):
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    shipping: Optional[float] = None
    total_amount: Optional[float] = None
    amount_due: Optional[float] = None


class PaymentDetails(StrictBaseModel):
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    iban: Optional[str] = None
    swift: Optional[str] = None
    payment_terms: Optional[str] = None


class InvoiceSchema(StrictBaseModel):
    invoice_details: InvoiceDetails = Field(default_factory=InvoiceDetails)
    vendor: Vendor = Field(default_factory=Vendor)
    bill_to: BillTo = Field(default_factory=BillTo)
    line_items: List[LineItem] = Field(default_factory=list)
    amounts: Amounts = Field(default_factory=Amounts)
    payment_details: PaymentDetails = Field(default_factory=PaymentDetails)
    contains_signature: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)


# =========================
# MEDICAL RECORD SCHEMA
# =========================

class Patient(StrictBaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    patient_id: Optional[str] = None


class Diagnosis(StrictBaseModel):
    condition: Optional[str] = None
    diagnosis_date: Optional[str] = None
    severity: Optional[str] = None


class Medication(StrictBaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Allergy(StrictBaseModel):
    allergen: Optional[str] = None
    reaction: Optional[str] = None
    severity: Optional[str] = None


class LabResult(StrictBaseModel):
    test_name: Optional[str] = None
    result: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    date: Optional[str] = None


class Procedure(StrictBaseModel):
    procedure_name: Optional[str] = None
    procedure_date: Optional[str] = None
    outcome: Optional[str] = None


class Physician(StrictBaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    contact: Optional[str] = None


class Hospital(StrictBaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class MedicalRecordSchema(StrictBaseModel):
    patient: Patient = Field(default_factory=Patient)
    medical_summary: Optional[str] = None
    diagnoses: List[Diagnosis] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    allergies: List[Allergy] = Field(default_factory=list)
    lab_results: List[LabResult] = Field(default_factory=list)
    procedures: List[Procedure] = Field(default_factory=list)
    physician: Physician = Field(default_factory=Physician)
    hospital: Hospital = Field(default_factory=Hospital)
    confidence: float = Field(0.0, ge=0.0, le=1.0)


# =========================
# CONTRACT SCHEMA
# =========================

class ContractDetails(StrictBaseModel):
    contract_number: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    renewal_terms: Optional[str] = None
    governing_law: Optional[str] = None


class Party(StrictBaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class PaymentTerms(StrictBaseModel):
    currency: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[str] = None
    payment_schedule: Optional[str] = None


class Obligation(StrictBaseModel):
    party: Optional[str] = None
    description: Optional[str] = None


class Clause(StrictBaseModel):
    clause: Optional[str] = None
    description: Optional[str] = None


class Signature(StrictBaseModel):
    party: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    date_signed: Optional[str] = None


class ContractSchema(StrictBaseModel):
    contract_details: ContractDetails = Field(default_factory=ContractDetails)
    parties: List[Party] = Field(default_factory=list)
    payment_terms: PaymentTerms = Field(default_factory=PaymentTerms)
    obligations: List[Obligation] = Field(default_factory=list)
    termination_clauses: List[Clause] = Field(default_factory=list)
    confidentiality_clauses: List[Clause] = Field(default_factory=list)
    signatures: List[Signature] = Field(default_factory=list)
    contains_signature: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)


# =========================
# NUMERIC FIELDS MAP
# =========================

NUMERIC_FIELDS_MAP = {
    "invoice": [
        "line_items.quantity",
        "line_items.unit_price",
        "line_items.total",
        "amounts.subtotal",
        "amounts.tax",
        "amounts.discount",
        "amounts.shipping",
        "amounts.total_amount",
        "amounts.amount_due"
    ],
    "contract": [
        "payment_terms.amount"
    ]
}


# =========================
# SCHEMA MAP
# =========================

SCHEMA_MAP = {
    "resume": ResumeSchema,
    "invoice": InvoiceSchema,
    "medical_record": MedicalRecordSchema,
    "contract": ContractSchema
}
