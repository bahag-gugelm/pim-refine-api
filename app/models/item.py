from ormar.models import Model
from ormar import JSON, String, ForeignKey, DateTime, UUID, Integer

from app.db import metadata, database, bdx_database
from app.models.user import UserModel

from sqlalchemy import func


class IceCatItemInfoModel(Model):
    class Meta:
        tablename = 'icecat_info'
        metadata = metadata
        database = database

    ean = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=13
        )
    info = JSON()
    requested_by = ForeignKey(UserModel)
    requested_at = DateTime(server_default=func.current_timestamp())


class CrawlabItemInfoModel(Model):
    class Meta:
        tablename = 'crawlab_info'
        metadata = metadata
        database = database

    ean = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=13,
        )
    info = JSON()
    task_id = UUID()


class PawInfoModel(Model):
    class Meta:
        tablename = 'paw_info'
        metadata = metadata
        database = database

    variant_id = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=15
        )
    info = JSON()

class PimQuery20_5(Model):
    class Meta:
        tablename = "PIM_aktuell_Query20_5_DE_view"
        database = bdx_database
        metadata = metadata

    Variant_product = String(max_length=15, primary_key=True)
    Base_product = String(max_length=9)		
    EAN = String(max_length=13)
    Product_name = String(max_length=400)		
    SAP_name = String(max_length=120)	
    Mandators = String(max_length=90)
    Suppliers = String(max_length=350)
    Main_material_group = String(max_length=1)	
    KSP = String(max_length=2)	
    Material_group_subgroup = String(max_length=5)
    Material_group_node = String(max_length=5)
    Material_group = String(max_length=75)
    SAP_status = String(max_length=13)
    Approval = String(max_length=12)
    Status_data_maintenance = String(max_length=35)
    Flag_status = String(max_length=12)
    Online_reservation = String(max_length=3)
    Maintenance_classification = String(max_length=2)
    Processed_by_tool = String(max_length=5)
    Initial_responsibility = String(max_length=20)
    General_responsibility = String(max_length=20)
    Private_brand___brand = String(max_length=50)
    Product_line = String(max_length=50)
    Product_name_category = String(max_length=50)
    Type_designation = String(max_length=80)
    Description = String(max_length=10000)
    USP_1 = String(max_length=110)
    USP_2 = String(max_length=110)
    USP_3 = String(max_length=110)
    USP_4 = String(max_length=110)
    USP_5 = String(max_length=110)
    Name_attributes = String(max_length=125)
    Primary_frontend_category = String(max_length=8)
    Secondary_frontend_categories = String(max_length=110)
    Count_available_images = String(max_length=5)
    Count_active_images = String(max_length=5)
    URL_main_image = String(max_length=100)
    AM_SystemCreated = DateTime()
    AM_SystemModified = DateTime()
    AM_ExcelFileWithPath = String(max_length=500)


class PimQuery29(Model):
    class Meta:
        tablename = "PIM_akutell_Query29_DE_view"
        database = bdx_database
        metadata = metadata
    
    Material_group = String(max_length=60)
    Variant_product = String(max_length=60)
    Mandators = String(max_length=33)
    SAP_name = String(max_length=75)
    Product_name_category = String(max_length=110)
    Classifying_category = String(max_length=80)
    Attribute_identifier = String(max_length=80)
    Attribute_name = String(max_length=80)
    Attribute_type = String(max_length=9)
    Value_identifier = String(max_length=300)
    Value_name = String(max_length=300)
    Value_unit = String(max_length=60)
    Value_position = String(max_length=4)
    Value_language = String(max_length=35, nullable=True)
    lfd_nr = Integer(primary_key=True)
    AM_SystemCreated = DateTime()
    AM_SystemModified = DateTime()
    AM_ExcelFileWithPath = String(max_length=500)
