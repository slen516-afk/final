from pydantic import BaseModel, Field

class CoverLetter(BaseModel):
    subject: str = Field(description="一個吸引人且專業的郵件主旨，需包含職位名稱與核心賣點")
    content: str = Field(description="求職信完整正文，包含問候、價值對標、行動呼籲，不含任何 Markdown 標記")
