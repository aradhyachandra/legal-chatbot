from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sample Indian Legal Document', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()
pdf.add_page()
pdf.chapter_title('THE INDIAN CONTRACT ACT, 1872')
pdf.chapter_body(
    "1. Short title.-This Act may be called the Indian Contract Act, 1872.\n"
    "Extent, Commencement.-It extends to the whole of India; and it shall come into force on the first day of September, 1872.\n\n"
    "2. Interpretation-clause.-In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context:-\n"
    "(a) When one person signifies to another his willingness to do or to abstain from doing anything, with a view to obtaining the assent of that other to such act or abstinence, he is said to make a proposal;\n"
    "(b) When the person to whom the proposal is made signifies his assent thereto, the proposal is said to be accepted. A proposal, when accepted, becomes a promise;\n"
    "(c) The person making the proposal is called the 'promisor', and the person accepting the proposal is called the 'promisee';\n"
    "(d) When, at the desire of the promisor, the promisee or any other person has done or abstained from doing, or does or abstains from doing, or promises to do or to abstain from doing, something, such act or abstinence or promise is called a consideration for the promise;\n"
    "(e) Every promise and every set of promises, forming the consideration for each other, is an agreement;\n"
    "(f) Promises which form the consideration or part of the consideration for each other are called reciprocal promises;\n"
    "(g) An agreement not enforceable by law is said to be void;\n"
    "(h) An agreement enforceable by law is a contract.\n"
)
pdf.chapter_title('Section 10. What agreements are contracts')
pdf.chapter_body(
    "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void.\n"
    "Nothing herein contained shall affect any law in force in India and not hereby expressly repealed by which any contract is required to be made in writing or in the presence of witnesses, or any law relating to the registration of documents."
)
pdf.output('data/raw/indian_contract_act_sample.pdf')
print("Created sample PDF at data/raw/indian_contract_act_sample.pdf")
