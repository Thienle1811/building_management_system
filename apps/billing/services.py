from django.db import transaction
from django.utils import timezone
from apps.buildings.models import Apartment
from apps.residents.models import Vehicle
from .models import MeterReading, ServiceConfig, PriceTier, Invoice, InvoiceItem, VehicleType

class BillingService:
    @staticmethod
    def create_monthly_meter_readings(month, year, service_types=['ELECTRICITY', 'WATER']):
        apartments = Apartment.objects.filter(status__in=['OCCUPIED', 'VACANT'])
        created_count = 0
        readings_to_create = []
        for apt in apartments:
            for s_type in service_types:
                if MeterReading.objects.filter(apartment=apt, service_type=s_type, record_month=month, record_year=year).exists():
                    continue
                old_index = BillingService.get_previous_index(apt, s_type, month, year)
                readings_to_create.append(MeterReading(
                    apartment=apt, service_type=s_type, record_month=month, record_year=year,
                    old_index=old_index, status='PENDING'
                ))
        if readings_to_create:
            MeterReading.objects.bulk_create(readings_to_create)
            created_count = len(readings_to_create)
        return created_count

    @staticmethod
    def get_previous_index(apartment, service_type, current_month, current_year):
        prev_month = current_month - 1
        prev_year = current_year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        prev_reading = MeterReading.objects.filter(
            apartment=apartment, service_type=service_type, record_month=prev_month, record_year=prev_year
        ).first()
        if prev_reading and prev_reading.new_index is not None:
            return prev_reading.new_index
        return 0

    @staticmethod
    def calculate_consumption_cost(consumption, service_type):
        config = ServiceConfig.objects.filter(service_type=service_type, is_active=True).first()
        if not config:
            return 0, "Chưa cấu hình giá"

        total_cost = 0
        details = []

        if config.calculation_method == 'FIXED_PER_UNIT':
            total_cost = consumption * config.flat_rate
            details.append(f"{consumption} x {config.flat_rate:,.0f}")

        elif config.calculation_method == 'TIERED':
            tiers = config.tiers.all().order_by('tier_level')
            remaining_consumption = consumption
            for tier in tiers:
                if remaining_consumption <= 0: break
                tier_range = (tier.max_value - tier.min_value + 1) if tier.max_value else remaining_consumption
                tier_usage = min(remaining_consumption, tier_range)
                cost = tier_usage * tier.price
                total_cost += cost
                details.append(f"Bậc {tier.tier_level} ({tier_usage} số): {cost:,.0f}đ")
                remaining_consumption -= tier_usage

        tax_str = ""
        if service_type == 'WATER':
            vat = total_cost * (config.vat_percent / 100)
            env_fee = total_cost * (config.environment_fee_percent / 100)
            total_cost += vat + env_fee
            tax_str = f" + VAT({config.vat_percent:g}%) + BVMT({config.environment_fee_percent:g}%)"

        return total_cost, f"{', '.join(details)}{tax_str}"

    @staticmethod
    def generate_monthly_invoices(month, year):
        apartments = Apartment.objects.filter(status='OCCUPIED')
        created_count = 0
        skipped_apartments = []

        for apt in apartments:
            if Invoice.objects.filter(apartment=apt, month=month, year=year).exists():
                continue

            has_pending = MeterReading.objects.filter(
                apartment=apt, record_month=month, record_year=year, status='PENDING'
            ).exists()
            has_record = MeterReading.objects.filter(
                apartment=apt, record_month=month, record_year=year
            ).exists()

            if has_pending or not has_record:
                skipped_apartments.append(apt.apartment_code)
                continue 

            with transaction.atomic():
                invoice = Invoice.objects.create(
                    code=f"INV-{year}{month:02d}-{apt.apartment_code}",
                    apartment=apt,
                    resident=apt.owner,
                    month=month,
                    year=year,
                    status='DRAFT'
                )
                total_invoice = 0

                # Tiền Điện/Nước
                readings = MeterReading.objects.filter(
                    apartment=apt, record_month=month, record_year=year, status='RECORDED'
                )
                for reading in readings:
                    cost, desc = BillingService.calculate_consumption_cost(reading.consumption, reading.service_type)
                    if cost > 0:
                        InvoiceItem.objects.create(
                            invoice=invoice, title=f"Tiền {reading.get_service_type_display()}",
                            amount=cost, description=f"Tiêu thụ: {reading.consumption}. {desc}"
                        )
                        total_invoice += cost
                        reading.status = 'BILLED'
                        reading.save()

                # Tiền Gửi xe
                vehicles = Vehicle.objects.filter(resident__current_apartment=apt)
                for vehicle in vehicles:
                    v_type = VehicleType.objects.filter(name__icontains=vehicle.vehicle_type).first()
                    price = v_type.monthly_price if v_type else 0
                    if price > 0:
                        InvoiceItem.objects.create(
                            invoice=invoice, title=f"Phí gửi xe {vehicle.license_plate}",
                            amount=price, description=f"Loại: {vehicle.vehicle_type}"
                        )
                        total_invoice += price

                # Tiền Thuê & Phí QL
                if apt.price > 0:
                     InvoiceItem.objects.create(invoice=invoice, title="Tiền thuê căn hộ", amount=apt.price, description="Theo hợp đồng")
                     total_invoice += apt.price

                mgt_config = ServiceConfig.objects.filter(service_type='MANAGEMENT', is_active=True).first()
                if mgt_config:
                    mgt_cost = 0
                    if mgt_config.calculation_method == 'PER_SQM' and apt.net_area:
                        mgt_cost = apt.net_area * mgt_config.flat_rate
                    elif mgt_config.calculation_method == 'FIXED_PER_MONTH':
                        mgt_cost = mgt_config.flat_rate
                    if mgt_cost > 0:
                        InvoiceItem.objects.create(
                            invoice=invoice, title="Phí quản lý vận hành", amount=mgt_cost, description=mgt_config.name
                        )
                        total_invoice += mgt_cost

                invoice.total_amount = total_invoice
                invoice.save()
                created_count += 1
        
        return created_count, skipped_apartments
    
    # --- PHẦN MỚI THÊM PHASE 5 ---
    @staticmethod
    def confirm_payment_by_id(invoice_id):
        """Xác nhận thanh toán hóa đơn theo ID từ giao diện Web BQL"""
        try:
            invoice = Invoice.objects.get(pk=invoice_id)
            if invoice.status != 'PAID':
                invoice.status = 'PAID'
                invoice.payment_date = timezone.now()
                invoice.payment_method = 'CASH' # Mặc định là cash nếu Admin bấm nút này mà không chọn method
                invoice.save()
                return True
            return False
        except Invoice.DoesNotExist:
            return False