import chift

from chift.openapi.openapi import (
    AccountBalanceFilter,
    AccountItem,
    AnalyticAccountItemIn,
    AnalyticAccountItemOutMultiAnalyticPlans,
    AnalyticAccountItemUpdate,
    AttachmentItem,
    BackboneCommonModelsInvoicingCommonInvoiceType,
    BoolParam,
    ChiftPageAccountBalance,
    ChiftPageAccountingCategoryItem,
    ChiftPageAccountingVatCode,
    ChiftPageAccountItem,
    ChiftPageAnalyticAccountItemOutMultiAnalyticPlans,
    ChiftPageAnalyticPlanItem,
    ChiftPageAttachmentItemOut,
    ChiftPageBalanceItemOut,
    ChiftPageCategoryItem,
    ChiftPageClientItemOut,
    ChiftPageCommerceCustomerItem,
    ChiftPageCommerceLocationItemOut,
    ChiftPageContactItemOut,
    ChiftPageEmployeeItem,
    ChiftPageInvoiceItemOut,
    ChiftPageInvoicingPaymentItem,
    ChiftPageInvoicingPaymentMethodItem,
    ChiftPageInvoicingVatCode,
    ChiftPageJournal,
    ChiftPageMiscellaneousOperationOut,
    ChiftPageOpportunityItem,
    ChiftPageOrderItemOut,
    ChiftPageOutstandingItem,
    ChiftPagePayment,
    ChiftPagePaymentItemOut,
    ChiftPagePaymentMethodItem,
    ChiftPagePaymentMethods,
    ChiftPagePMSAccountingCategoryItem,
    ChiftPagePMSCustomerItem,
    ChiftPagePMSInvoiceFullItem,
    ChiftPagePMSLocationItem,
    ChiftPagePMSOrderItem,
    ChiftPagePMSPaymentItem,
    ChiftPagePMSPaymentMethods,
    ChiftPagePMSTaxRateItem,
    ChiftPagePOSCustomerItem,
    ChiftPagePOSLocationItem,
    ChiftPagePOSOrderItem,
    ChiftPagePOSPaymentItem,
    ChiftPagePOSProductItem,
    ChiftPageProductCategoryItem,
    ChiftPageProductItem,
    ChiftPageProductItemOut,
    ChiftPageRefundItemOut,
    ChiftPageSupplierItemOut,
    ChiftPageTaxRateItem,
    ChiftPageTransactionItemOut,
    ClientItemIn,
    ClientItemOut,
    ClientItemUpdate,
    ClosureItem,
    CommerceCustomerItem,
    ContactItemIn,
    ContactItemOut,
    ContactType,
    DocumentType,
    FinancialEntryItemIn,
    FinancialEntryItemInOld,
    FinancialEntryItemOut,
    FinancialEntryItemOutOld,
    GenericJournalEntry,
    InvoiceItemInput,
    InvoiceItemOut,
    InvoiceItemOutMultiAnalyticPlans,
    InvoiceItemOutSingle,
    InvoicingVatCode,
    Journal,
    JournalEntryMultiAnalyticPlan,
    JournalIn,
    LedgerAccountItemIn,
    MatchingIn,
    MatchingOut,
    MiscellaneousOperationIn,
    MiscellaneousOperationOut,
    MiscellaneousOperationStatusIn,
    MultipleMatchingIn,
    OpportunityItem,
    OrderItemOut,
    OutstandingType,
    PaymentItemOut,
    PaymentStatusInput,
    PMSClosureItem,
    PMSCustomerItem,
    PMSStates,
    POSCreateCustomerItem,
    POSCustomerItem,
    POSOrderItem,
    ProductItemInput,
    ProductItemOut,
    ProductItemOutput,
    SalesItem,
    SupplierItemIn,
    SupplierItemOut,
    SupplierItemUpdate,
    TransactionAccountingCategory,
    VariantItem,
)


def accounting_get_analytic_plans(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPageAnalyticPlanItem:
    """Get analytic plans from the accounting system

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results

    Returns:
        ChiftPageAnalyticPlanItem: Paginated list of analytic plans
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticPlan.all(
        params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_create_analytic_account_multi_plans(
    consumer_id: str,
    analytic_plan: str,
    data: AnalyticAccountItemIn,
    folder_id: str | None = None,
) -> AnalyticAccountItemOutMultiAnalyticPlans:
    """Create a new analytic account in a specific analytic plan

    Args:
        consumer_id (str): The consumer ID
        analytic_plan (str): Analytic plan identifier
        data (AnalyticAccountItemIn): Analytic account data
        folder_id (str): Optional folder ID for organization

    Returns:
        AnalyticAccountItemOutMultiAnalyticPlans: The created analytic account
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticAccountMultiPlan.create(
        data=data, analytic_plan=analytic_plan, params={"folder_id": folder_id}
    )


def accounting_get_analytic_accounts_multi_plans(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPageAnalyticAccountItemOutMultiAnalyticPlans:
    """Returns all analytic accounts of all analytic plans

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results

    Returns:
        ChiftPageAnalyticAccountItemOutMultiAnalyticPlans: Paginated list of analytic accounts
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticAccountMultiPlan.all(
        params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_get_analytic_account_multi_plans(
    consumer_id: str, analytic_account_id: str, analytic_plan: str, folder_id: str | None = None
) -> AnalyticAccountItemOutMultiAnalyticPlans:
    """Returns one specific analytic account of a specific analytic plan

    Args:
        consumer_id (str): The consumer ID
        analytic_account_id (str): Unique identifier of the analytic account
        analytic_plan (str): Analytic plan identifier
        folder_id (str): Optional folder ID for context

    Returns:
        AnalyticAccountItemOutMultiAnalyticPlans: The requested analytic account
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticAccountMultiPlan.get(
        analytic_account_id, analytic_plan=analytic_plan, params={"folder_id": folder_id}
    )


def accounting_update_analytic_account_multi_plans(
    consumer_id: str,
    analytic_account_id: str,
    analytic_plan: str,
    data: AnalyticAccountItemUpdate,
    folder_id: str | None = None,
) -> AnalyticAccountItemOutMultiAnalyticPlans:
    """Update one specific analytic account in a specific analytic plan

    Args:
        consumer_id (str): The consumer ID
        analytic_account_id (str): Unique identifier of the analytic account
        analytic_plan (str): Analytic plan identifier
        data (AnalyticAccountItemUpdate): Updated analytic account data
        folder_id (str): Optional folder ID for context

    Returns:
        AnalyticAccountItemOutMultiAnalyticPlans: The updated analytic account
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticAccountMultiPlan.update(
        analytic_account_id, data=data, analytic_plan=analytic_plan, params={"folder_id": folder_id}
    )


def accounting_delete_analytic_account_multi_plans(
    consumer_id: str, analytic_plan: str, analytic_account_id: str, folder_id: str | None = None
) -> bool:
    """Delete an analytic account

    Args:
        consumer_id (str): The consumer ID
        analytic_plan (str): Analytic plan identifier
        analytic_account_id (str): Unique identifier of the analytic account
        folder_id (str): Optional folder ID for context

    Returns:
        bool: True if the account was successfully deleted
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.AnalyticAccountMultiPlan.delete(
        analytic_account_id, analytic_plan=analytic_plan, params={"folder_id": folder_id}
    )


def accounting_create_client(
    consumer_id: str,
    data: ClientItemIn,
    folder_id: str | None = None,
    force_merge: str | None = None,
) -> ClientItemOut:
    """Create a new client

    Args:
        consumer_id (str): The consumer ID
        data (ClientItemIn): Client data
        folder_id (str): Optional folder ID for organization
        force_merge (str): Force merge if client exists

    Returns:
        ClientItemOut: The created client
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Client.create(
        data=data, params={"folder_id": folder_id, "force_merge": force_merge}
    )


def accounting_get_clients(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    search: str | None = None,
    updated_after: str | None = None,
) -> ChiftPageClientItemOut:
    """Returns a list of accounting clients

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        search (str): Search term for filtering clients
        updated_after (str): Filter clients updated after this datetime

    Returns:
        ChiftPageClientItemOut: Paginated list of clients
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Client.all(
        params={
            "page": page,
            "size": size,
            "folder_id": folder_id,
            "search": search,
            "updated_after": updated_after,
        }
    )


def accounting_get_client(
    consumer_id: str, client_id: str, folder_id: str | None = None
) -> ClientItemOut:
    """Returns a specific accounting client

    Args:
        consumer_id (str): The consumer ID
        client_id (str): Unique identifier of the client
        folder_id (str): Optional folder ID for context

    Returns:
        ClientItemOut: The requested client
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Client.get(client_id, params={"folder_id": folder_id})


def accounting_update_client(
    consumer_id: str, client_id: str, data: ClientItemUpdate, folder_id: str | None = None
) -> ClientItemOut:
    """Update an accounting client

    Args:
        consumer_id (str): The consumer ID
        client_id (str): Unique identifier of the client
        data (ClientItemUpdate): Updated client data
        folder_id (str): Optional folder ID for context

    Returns:
        ClientItemOut: The updated client
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Client.update(client_id, data=data, params={"folder_id": folder_id})


def accounting_create_supplier(
    consumer_id: str,
    data: SupplierItemIn,
    folder_id: str | None = None,
    force_merge: str | None = None,
) -> SupplierItemOut:
    """Create a new supplier

    Args:
        consumer_id (str): The consumer ID
        data (SupplierItemIn): Supplier data
        folder_id (str): Optional folder ID for organization
        force_merge (str): Force merge if supplier exists

    Returns:
        SupplierItemOut: The created supplier
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Supplier.create(
        data=data, params={"folder_id": folder_id, "force_merge": force_merge}
    )


def accounting_get_suppliers(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    search: str | None = None,
    updated_after: str | None = None,
) -> ChiftPageSupplierItemOut:
    """Returns a list of accounting suppliers

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        search (str): Search term for filtering suppliers
        updated_after (str): Filter suppliers updated after this datetime

    Returns:
        ChiftPageSupplierItemOut: Paginated list of suppliers
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Supplier.all(
        params={
            "page": page,
            "size": size,
            "folder_id": folder_id,
            "search": search,
            "updated_after": updated_after,
        }
    )


def accounting_get_supplier(
    consumer_id: str, supplier_id: str, folder_id: str | None = None
) -> SupplierItemOut:
    """Returns one accounting supplier

    Args:
        consumer_id (str): The consumer ID
        supplier_id (str): Unique identifier of the supplier
        folder_id (str): Optional folder ID for context

    Returns:
        SupplierItemOut: The requested supplier
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Supplier.get(supplier_id, params={"folder_id": folder_id})


def accounting_update_supplier(
    consumer_id: str, supplier_id: str, data: SupplierItemUpdate, folder_id: str | None = None
) -> SupplierItemOut:
    """Update an accounting supplier

    Args:
        consumer_id (str): The consumer ID
        supplier_id (str): Unique identifier of the supplier
        data (SupplierItemUpdate): Updated supplier data
        folder_id (str): Optional folder ID for context

    Returns:
        SupplierItemOut: The updated supplier
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Supplier.update(
        supplier_id, data=data, params={"folder_id": folder_id}
    )


def accounting_get_invoice_multi_analytic_plans(
    consumer_id: str,
    invoice_id: str,
    folder_id: str | None = None,
    include_payments: str | None = BoolParam.false,
    include_invoice_lines: str | None = BoolParam.false,
) -> InvoiceItemOutMultiAnalyticPlans:
    """Returns a specific invoice with invoice lines including multiple analytic plans

    Args:
        consumer_id (str): The consumer ID
        invoice_id (str): Unique identifier of the invoice
        folder_id (str): Optional folder ID for context
        include_payments (str): Include payment information in response ("true", "false")
        include_invoice_lines (str): Include invoice line details in response ("true", "false")

    Returns:
        InvoiceItemOutMultiAnalyticPlans: The requested invoice with multi-analytic plan details
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Invoice.get(
        invoice_id,
        params={
            "folder_id": folder_id,
            "include_payments": include_payments,
            "include_invoice_lines": include_invoice_lines,
        },
    )


def accounting_get_payments_by_invoice(
    consumer_id: str,
    invoice_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPagePayment:
    """Get payments of a specific invoice based on its ID

    Args:
        consumer_id (str): The consumer ID
        invoice_id (str): Unique identifier of the invoice
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID for context

    Returns:
        ChiftPagePayment: Paginated list of invoice payments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Invoice.all(
        invoice_id=invoice_id, params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_get_chart_of_accounts(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    classes: str | None = None,
) -> ChiftPageAccountItem:
    """Get all accounts in the chart of accounts

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        classes (str): Filter by account classes

    Returns:
        ChiftPageAccountItem: Paginated list of chart of accounts
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Account.all(
        params={"page": page, "size": size, "folder_id": folder_id, "classes": classes}
    )


def accounting_create_ledger_account(
    consumer_id: str, data: LedgerAccountItemIn, folder_id: str | None = None
) -> AccountItem:
    """Create a new ledger account in the chart of accounts

    Args:
        consumer_id (str): The consumer ID
        data (LedgerAccountItemIn): Ledger account data with name and number
        folder_id (str): Optional folder ID for organization

    Returns:
        AccountItem: The created ledger account
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Account.create(data=data, params={"folder_id": folder_id})


def accounting_get_account(
    consumer_id: str, account_id: str, folder_id: str | None = None
) -> AccountItem:
    """Returns a specific account from the chart of accounts

    Args:
        consumer_id (str): The consumer ID
        account_id (str): Unique identifier of the account
        folder_id (str): Optional folder ID for context

    Returns:
        AccountItem: The requested account
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Account.get(account_id, params={"folder_id": folder_id})


def accounting_get_accounts_balances(
    consumer_id: str,
    data: AccountBalanceFilter,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPageAccountBalance:
    """Get the balance of accounts in the accounting plan between specific months

    Args:
        consumer_id (str): The consumer ID
        data (AccountBalanceFilter): Filter criteria with accounts and date range
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID for context

    Returns:
        ChiftPageAccountBalance: Paginated list of account balances
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Account.all(
        data=data, params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_get_journals(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPageJournal:
    """Get journals existing in the accounting system

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results

    Returns:
        ChiftPageJournal: Paginated list of journals
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Journal.all(
        params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_create_journal(
    consumer_id: str, data: JournalIn, folder_id: str | None = None
) -> Journal:
    """Create a journal in the accounting system

    Args:
        consumer_id (str): The consumer ID
        data (JournalIn): Journal data
        folder_id (str): Optional folder ID for organization

    Returns:
        Journal: The created journal
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Journal.create(data=data, params={"folder_id": folder_id})


def accounting_get_journal(
    consumer_id: str, journal_id: str, folder_id: str | None = None
) -> Journal:
    """Returns a specific journal by ID

    Args:
        consumer_id (str): The consumer ID
        journal_id (str): Unique identifier of the journal
        folder_id (str): Optional folder ID for context

    Returns:
        Journal: The requested journal
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Journal.get(journal_id, params={"folder_id": folder_id})


def accounting_create_generic_journal_entry(
    consumer_id: str,
    data: GenericJournalEntry,
    folder_id: str | None = None,
    force_currency_exchange: str | None = BoolParam.false,
) -> JournalEntryMultiAnalyticPlan:
    """Create a new Journal Entry in the accounting system

    Args:
        consumer_id (str): The consumer ID
        data (GenericJournalEntry): Journal entry data
        folder_id (str): Optional folder ID for organization
        force_currency_exchange (str): Force currency exchange calculation ("true", "false")

    Returns:
        JournalEntryMultiAnalyticPlan: The created journal entry
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.JournalEntry.create(
        data=data,
        params={"folder_id": folder_id, "force_currency_exchange": force_currency_exchange},
    )


def accounting_get_vat_codes(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    scope: str | None = None,
) -> ChiftPageAccountingVatCode:
    """Get VAT codes existing in the accounting system

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        scope (str): Filter by scope (sale, purchase, both)

    Returns:
        ChiftPageAccountingVatCode: Paginated list of VAT codes
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Tax.all(
        params={"page": page, "size": size, "folder_id": folder_id, "scope": scope}
    )


def accounting_create_miscellaneous_operation(
    consumer_id: str, data: MiscellaneousOperationIn, folder_id: str | None = None
) -> MiscellaneousOperationOut:
    """Create a new miscellaneous operation

    Args:
        consumer_id (str): The consumer ID
        data (MiscellaneousOperationIn): Miscellaneous operation data
        folder_id (str): Optional folder ID for organization

    Returns:
        MiscellaneousOperationOut: The created miscellaneous operation
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.MiscellaneousOperation.create(
        data=data, params={"folder_id": folder_id}
    )


def accounting_get_miscellaneous_operations(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    journal_ids: str | None = None,
    updated_after: str | None = None,
    status: MiscellaneousOperationStatusIn | None = None,
) -> ChiftPageMiscellaneousOperationOut:
    """Get miscellaneous operations from the accounting system

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        journal_ids (str): Filter by specific journal IDs
        updated_after (str): Filter operations updated after this datetime
        status (str): Filter by status (draft, posted, cancelled)

    Returns:
        ChiftPageMiscellaneousOperationOut: Paginated list of miscellaneous operations
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.MiscellaneousOperation.all(
        params={
            "page": page,
            "size": size,
            "folder_id": folder_id,
            "date_from": date_from,
            "date_to": date_to,
            "journal_ids": journal_ids,
            "updated_after": updated_after,
            "status": status,
        }
    )


def accounting_get_miscellaneous_operation(
    consumer_id: str, operation_id: str, folder_id: str | None = None
) -> MiscellaneousOperationOut:
    """Get a specific miscellaneous operation by ID

    Args:
        consumer_id (str): The consumer ID
        operation_id (str): Unique identifier of the miscellaneous operation
        folder_id (str): Optional folder ID for context

    Returns:
        MiscellaneousOperationOut: The requested miscellaneous operation
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.MiscellaneousOperation.get(
        operation_id, params={"folder_id": folder_id}
    )


def accounting_create_financial_entry(
    consumer_id: str,
    data: FinancialEntryItemInOld,
    folder_id: str | None = None,
    financial_counterpart_account: str | None = None,
) -> FinancialEntryItemOutOld:
    """Create a new financial entry (Bank or Cash operation)

    Args:
        consumer_id (str): The consumer ID
        data (FinancialEntryItemInOld): Financial entry data
        folder_id (str): Optional folder ID for organization
        financial_counterpart_account (str): Counterpart account for the operation

    Returns:
        FinancialEntryItemOutOld: The created financial entry
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.FinancialEntry.create(
        data=data,
        params={
            "folder_id": folder_id,
            "financial_counterpart_account": financial_counterpart_account,
        },
    )


def accounting_create_financial_entries(
    consumer_id: str,
    data: FinancialEntryItemIn,
    folder_id: str | None = None,
    financial_counterpart_account: str | None = None,
) -> FinancialEntryItemOut:
    """Create a new financial entry (Bank or Cash operation)

    Args:
        consumer_id (str): The consumer ID
        data (FinancialEntryItemIn): Financial entry data
        folder_id (str): Optional folder ID for organization
        financial_counterpart_account (str): Counterpart account for the operation

    Returns:
        FinancialEntryItemOut: The created financial entry
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.FinancialEntry.create(
        data=data,
        params={
            "folder_id": folder_id,
            "financial_counterpart_account": financial_counterpart_account,
        },
    )


def accounting_match_entries(
    consumer_id: str, data: MatchingIn, folder_id: str | None = None
) -> MatchingOut:
    """Match existing entries in the accounting system

    Args:
        consumer_id (str): The consumer ID
        data (MatchingIn): Matching data with entries and partner ID
        folder_id (str): Optional folder ID for context

    Returns:
        MatchingOut: The matching result
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    # Fixed: Use EntryMatching instead of Matching
    return consumer.accounting.EntryMatching.create(data=data, params={"folder_id": folder_id})


def accounting_match_entries_multiple(
    consumer_id: str, data: MultipleMatchingIn, folder_id: str | None = None
) -> list:
    """Match multiple existing entries in the accounting system

    Args:
        consumer_id (str): The consumer ID
        data (MultipleMatchingIn): Multiple matching data
        folder_id (str): Optional folder ID for context

    Returns:
        list: List of matching results
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.MultipleEntryMatching.create(
        data=data, params={"folder_id": folder_id}
    )


def accounting_get_outstandings(
    consumer_id: str,
    type: OutstandingType,
    unposted_allowed: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
    partner_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ChiftPageOutstandingItem:
    """Returns outstanding items (receivables/payables) from the accounting system

    Args:
        consumer_id (str): The consumer ID
        type (OutstandingType): Type of outstanding ("client", "supplier")
        unposted_allowed (str): Include unposted entries ("true", "false")
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results
        partner_id (str): Filter by specific partner ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format

    Returns:
        ChiftPageOutstandingItem: Paginated list of outstanding items
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Outstanding.all(
        params={
            "type": type,
            "unposted_allowed": unposted_allowed,
            "page": page,
            "size": size,
            "folder_id": folder_id,
            "partner_id": partner_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )


def accounting_get_employees(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    folder_id: str | None = None,
) -> ChiftPageEmployeeItem:
    """Returns a list of employees linked to the company

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        folder_id (str): Optional folder ID to filter results

    Returns:
        ChiftPageEmployeeItem: Paginated list of employees
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Employee.all(
        params={"page": page, "size": size, "folder_id": folder_id}
    )


def accounting_add_attachment(
    consumer_id: str,
    invoice_id: str,
    data: AttachmentItem,
    folder_id: str | None = None,
    overwrite_existing: str | None = BoolParam.false,
) -> bool:
    """Attach a document (PDF) to the invoice entry

    Args:
        consumer_id (str): The consumer ID
        invoice_id (str): Unique identifier of the invoice
        data (AttachmentItem): Attachment data with base64 string
        folder_id (str): Optional folder ID for context
        overwrite_existing (str): Overwrite existing attachment if exists ("true", "false")

    Returns:
        bool: True if attachment was successfully added
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Attachment.create(
        invoice_id,
        data=data,
        params={"folder_id": folder_id, "overwrite_existing": overwrite_existing},
    )


def accounting_get_attachments(
    consumer_id: str,
    type: DocumentType,
    document_id: str,
    folder_id: str | None = None,
    page: int | None = 1,
    size: int | None = 50,
) -> ChiftPageAttachmentItemOut:
    """Returns a list of all attachments linked to an accounting entry

    Args:
        consumer_id (str): The consumer ID
        type (DocumentType): Type of document the attachment is linked to ("invoice", "entry")
        document_id (str): Unique identifier of the document
        folder_id (str): Optional folder ID for context
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageAttachmentItemOut: Paginated list of attachments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.accounting.Attachment.all(
        params={
            "folder_id": folder_id,
            "type": type,
            "document_id": document_id,
            "page": page,
            "size": size,
        }
    )


def pos_get_customers(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    search: str | None = None,
    email: str | None = None,
    phone: str | None = None,
) -> ChiftPagePOSCustomerItem:
    """Returns the list of customers

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        search (str): Search term
        email (str): Email filter
        phone (str): Phone filter

    Returns:
        ChiftPagePOSCustomerItem: Paginated list of POS customers
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Customer.all(
        params={"page": page, "size": size, "search": search, "email": email, "phone": phone}
    )


def pos_create_customer(consumer_id: str, data: POSCreateCustomerItem) -> POSCustomerItem:
    """Create a customer

    Args:
        consumer_id (str): The consumer ID
        data (POSCreateCustomerItem): The request data

    Returns:
        POSCustomerItem: The created customer
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Customer.create(data=data)


def pos_get_customer(consumer_id: str, customer_id: str) -> POSCustomerItem:
    """Returns a specific customer

    Args:
        consumer_id (str): The consumer ID
        customer_id (str): Customer ID

    Returns:
        POSCustomerItem: The requested customer
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Customer.get(customer_id)


def pos_get_orders(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    date_from: str | None = None,
    date_to: str | None = None,
    location_id: str | None = None,
    customer_id: str | None = None,
) -> ChiftPagePOSOrderItem:
    """Returns the list of orders

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        date_from (str): Start date filter
        date_to (str): End date filter
        location_id (str): Location filter
        customer_id (str): Customer filter

    Returns:
        ChiftPagePOSOrderItem: Paginated list of POS orders
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Order.all(
        params={
            "page": page,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "location_id": location_id,
            "customer_id": customer_id,
        }
    )


def pos_get_order(consumer_id: str, order_id: str) -> POSOrderItem:
    """Returns a specific order

    Args:
        consumer_id (str): The consumer ID
        order_id (str): Order ID

    Returns:
        POSOrderItem: The requested order
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Order.get(order_id)


def pos_get_payments(
    consumer_id: str,
    date_from: str,
    date_to: str,
    page: int | None = 1,
    size: int | None = 50,
) -> ChiftPagePOSPaymentItem:
    """Returns a list of payments

    Args:
        consumer_id (str): The consumer ID
        date_from (str): Start date
        date_to (str): End date
        page (int): Page number
        size (int): Page size

    Returns:
        ChiftPagePOSPaymentItem: Paginated list of POS payments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Payment.all(
        params={"page": page, "size": size, "date_from": date_from, "date_to": date_to}
    )


def pos_get_payment_methods(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
) -> ChiftPagePaymentMethods:
    """Returns the list of payment methods

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        location_id (str): Location filter

    Returns:
        ChiftPagePaymentMethods: Paginated list of POS payment methods
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.PaymentMethod.all(
        params={"page": page, "size": size, "location_id": location_id}
    )


def pos_get_locations(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePOSLocationItem:
    """Returns the list of locations

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size

    Returns:
        ChiftPagePOSLocationItem: Paginated list of POS locations
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Location.all(params={"page": page, "size": size})


def pos_get_products(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
) -> ChiftPagePOSProductItem:
    """Returns a list of products

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        location_id (str): Location filter

    Returns:
        ChiftPagePOSProductItem: Paginated list of POS products
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Product.all(params={"page": page, "size": size, "location_id": location_id})


def pos_get_product_categories(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
    only_parents: str | None = BoolParam.false,
) -> ChiftPageProductCategoryItem:
    """Returns a list of product categories

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        location_id (str): Location filter
        only_parents (str): Only parent categories

    Returns:
        ChiftPageProductCategoryItem: Paginated list of POS product categories
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.ProductCategory.all(
        params={
            "page": page,
            "size": size,
            "location_id": location_id,
            "only_parents": only_parents,
        }
    )


def pos_get_accounting_categories(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
) -> ChiftPageAccountingCategoryItem:
    """Returns a list of accounting categories

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number
        size (int): Page size
        location_id (str): Location filter

    Returns:
        ChiftPageAccountingCategoryItem: Paginated list of POS accounting categories
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.AccountingCategory.all(
        params={"page": page, "size": size, "location_id": location_id}
    )


def pos_get_sales(
    consumer_id: str, date_from: str, date_to: str, location_id: str | None = None
) -> SalesItem:
    """Returns the summary of the sales

    Args:
        consumer_id (str): The consumer ID
        date_from (str): Start date
        date_to (str): End date
        location_id (str): Location filter

    Returns:
        SalesItem: Sales summary data
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Sale.all(
        params={"date_from": date_from, "date_to": date_to, "location_id": location_id}
    )


def pos_get_closure(consumer_id: str, date: str, location_id: str | None = None) -> ClosureItem:
    """Returns whether the closure was already done for a specific day

    Args:
        consumer_id (str): The consumer ID
        date (str): Date to check
        location_id (str): Location filter

    Returns:
        ClosureItem: Closure status information
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pos.Closure.get(date=date, params={"location_id": location_id})


def ecommerce_get_customers(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageCommerceCustomerItem:
    """Returns a list of all the customers

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageCommerceCustomerItem: Paginated list of e-commerce customers
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Customer.all(params={"page": page, "size": size})


def ecommerce_get_customer(consumer_id: str, customer_id: str) -> CommerceCustomerItem:
    """Returns a specific customer

    Args:
        consumer_id (str): The consumer ID
        customer_id (str): Unique identifier of the customer

    Returns:
        CommerceCustomerItem: The requested customer
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Customer.get(customer_id)


def ecommerce_get_products(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageProductItem:
    """Returns a list of all the products

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageProductItem: Paginated list of e-commerce products
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Product.all(params={"page": page, "size": size})


def ecommerce_get_product(consumer_id: str, product_id: str) -> ProductItemOutput:
    """Returns a specific product

    Args:
        consumer_id (str): The consumer ID
        product_id (str): Unique identifier of the product

    Returns:
        ProductItemOutput: The requested product
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Product.get(product_id)


def ecommerce_get_variants(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    product_id: str | None = None,
):
    """Returns a list of product variants

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        product_id (str): Optional product ID to filter variants

    Returns:
        List of product variants
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    params = {"page": page, "size": size, "product_id": product_id}
    return consumer.commerce.Variant.all(params=params)


def ecommerce_get_variant(consumer_id: str, variant_id: str) -> VariantItem:
    """Returns a specific product variant

    Args:
        consumer_id (str): The consumer ID
        variant_id (str): Unique identifier of the variant

    Returns:
        VariantItem: The requested product variant
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Variant.get(variant_id)


def ecommerce_get_locations(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageCommerceLocationItemOut:
    """Returns a list of all locations

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageCommerceLocationItemOut: Paginated list of e-commerce locations
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Location.all(params={"page": page, "size": size})


def ecommerce_get_orders(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    date_from: str | None = None,
    date_to: str | None = None,
    updated_after: str | None = None,
    include_detailed_refunds: str | None = BoolParam.false,
    include_product_categories: str | None = BoolParam.false,
    include_customer_details: str | None = BoolParam.true,
) -> ChiftPageOrderItemOut:
    """Returns a list of all the orders

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        updated_after (str): Filter orders updated after this datetime
        include_detailed_refunds (str): Include detailed refund information ("true", "false")
        include_product_categories (str): Include product category information ("true", "false")
        include_customer_details (str): Include customer details ("true", "false")

    Returns:
        ChiftPageOrderItemOut: Paginated list of e-commerce orders
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Order.all(
        params={
            "page": page,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "updated_after": updated_after,
            "include_detailed_refunds": include_detailed_refunds,
            "include_product_categories": include_product_categories,
            "include_customer_details": include_customer_details,
        }
    )


def ecommerce_get_order(
    consumer_id: str, order_id: str, include_product_categories: str | None = BoolParam.false
) -> OrderItemOut:
    """Returns a specific order

    Args:
        consumer_id (str): The consumer ID
        order_id (str): Unique identifier of the order
        include_product_categories (str): Include product category information ("true", "false")

    Returns:
        OrderItemOut: The requested order
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Order.get(
        order_id, params={"include_product_categories": include_product_categories}
    )


def ecommerce_get_payment_methods(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePaymentMethodItem:
    """Returns the list of the payment methods

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePaymentMethodItem: Paginated list of e-commerce payment methods
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.PaymentMethod.all(params={"page": page, "size": size})


def ecommerce_get_product_categories(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    only_parents: str | None = BoolParam.false,
) -> ChiftPageCategoryItem:
    """Returns the list of the product categories

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        only_parents (str): Only return parent categories ("true", "false")

    Returns:
        ChiftPageCategoryItem: Paginated list of e-commerce product categories
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.ProductCategory.all(
        params={"page": page, "size": size, "only_parents": only_parents}
    )


def ecommerce_get_taxes(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageTaxRateItem:
    """Returns the list of all tax rates

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageTaxRateItem: Paginated list of e-commerce tax rates
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.commerce.Tax.all(params={"page": page, "size": size})


def invoicing_get_invoices(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    date_from: str | None = None,
    date_to: str | None = None,
    invoice_type: BackboneCommonModelsInvoicingCommonInvoiceType
    | None = BackboneCommonModelsInvoicingCommonInvoiceType.all,
    payment_status: str | None = PaymentStatusInput.all,
    updated_after: str | None = None,
    include_invoice_lines: str | None = BoolParam.false,
) -> ChiftPageInvoiceItemOut:
    """Returns a list of invoices

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        invoice_type (BackboneCommonModelsInvoicingCommonInvoiceType): Filter by invoice type
        payment_status (str): Filter by payment status
        updated_after (str): Filter invoices updated after this datetime
        include_invoice_lines (str): Include invoice line details ("true", "false")

    Returns:
        ChiftPageInvoiceItemOut: Paginated list of invoices
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Invoice.all(
        params={
            "page": page,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "invoice_type": invoice_type,
            "payment_status": payment_status,
            "updated_after": updated_after,
            "include_invoice_lines": include_invoice_lines,
        }
    )


def invoicing_create_invoice(consumer_id: str, data: InvoiceItemInput) -> InvoiceItemOut:
    """Create a new invoice

    Args:
        consumer_id (str): The consumer ID
        data (InvoiceItemInput): Invoice data to create

    Returns:
        InvoiceItemOut: The created invoice
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Invoice.create(data=data)


def invoicing_get_invoice(
    consumer_id: str, invoice_id: str, include_pdf: str | None = BoolParam.false
) -> InvoiceItemOutSingle:
    """Returns an invoice

    Args:
        consumer_id (str): The consumer ID
        invoice_id (str): Unique identifier of the invoice
        include_pdf (str): Include PDF data in response ("true", "false")

    Returns:
        InvoiceItemOutSingle: The requested invoice
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Invoice.get(invoice_id, params={"include_pdf": include_pdf})


def invoicing_get_products(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageProductItemOut:
    """Returns a list of all the products

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageProductItemOut: Paginated list of invoicing products
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Product.all(params={"page": page, "size": size})


def invoicing_create_product(consumer_id: str, data: ProductItemInput) -> ProductItemOut:
    """Create a new product

    Args:
        consumer_id (str): The consumer ID
        data (ProductItemInput): Product data to create

    Returns:
        ProductItemOut: The created product
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Product.create(data=data)


def invoicing_get_product(consumer_id: str, product_id: str) -> ProductItemOut:
    """Returns a product

    Args:
        consumer_id (str): The consumer ID
        product_id (str): Unique identifier of the product

    Returns:
        ProductItemOut: The requested product
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Product.get(product_id)


def invoicing_get_contacts(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    contact_type: ContactType | None = ContactType.all,
) -> ChiftPageContactItemOut:
    """Returns a list of all the contacts

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        contact_type (ContactType): Filter by contact type

    Returns:
        ChiftPageContactItemOut: Paginated list of contacts
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Contact.all(
        params={"page": page, "size": size, "contact_type": contact_type}
    )


def invoicing_create_contact(consumer_id: str, data: ContactItemIn) -> ContactItemOut:
    """Create a new contact

    Args:
        consumer_id (str): The consumer ID
        data (ContactItemIn): Contact data to create

    Returns:
        ContactItemOut: The created contact
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Contact.create(data=data)


def invoicing_get_contact(consumer_id: str, contact_id: str) -> ContactItemOut:
    """Returns a contact

    Args:
        consumer_id (str): The consumer ID
        contact_id (str): Unique identifier of the contact

    Returns:
        ContactItemOut: The requested contact
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Contact.get(contact_id)


def invoicing_get_opportunities(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageOpportunityItem:
    """Returns a list of all the opportunities

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageOpportunityItem: Paginated list of opportunities
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Opportunity.all(params={"page": page, "size": size})


def invoicing_create_opportunity(consumer_id: str, data) -> OpportunityItem:
    """Create a new opportunity

    Args:
        consumer_id (str): The consumer ID
        data: Opportunity data to create

    Returns:
        OpportunityItem: The created opportunity
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Opportunity.create(data=data)


def invoicing_get_opportunity(consumer_id: str, opportunity_id: str) -> OpportunityItem:
    """Returns an opportunity

    Args:
        consumer_id (str): The consumer ID
        opportunity_id (str): Unique identifier of the opportunity

    Returns:
        OpportunityItem: The requested opportunity
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Opportunity.get(opportunity_id)


def invoicing_get_taxes(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageInvoicingVatCode:
    """Returns a list of all the taxes

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageInvoicingVatCode: Paginated list of invoicing taxes
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Tax.all(params={"page": page, "size": size})


def invoicing_get_tax(consumer_id: str, tax_id: str) -> InvoicingVatCode:
    """Returns a tax

    Args:
        consumer_id (str): The consumer ID
        tax_id (str): Unique identifier of the tax

    Returns:
        InvoicingVatCode: The requested tax
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Tax.get(tax_id)


def invoicing_get_payments(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ChiftPageInvoicingPaymentItem:
    """Returns a list of payments

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format

    Returns:
        ChiftPageInvoicingPaymentItem: Paginated list of invoicing payments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Payment.all(
        params={"page": page, "size": size, "date_from": date_from, "date_to": date_to}
    )


def invoicing_get_payment_methods(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageInvoicingPaymentMethodItem:
    """Returns the list of payment methods

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageInvoicingPaymentMethodItem: Paginated list of invoicing payment methods
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.PaymentMethod.all(params={"page": page, "size": size})


def invoicing_upload_document(consumer_id: str, data: AttachmentItem):
    """Upload a document

    Args:
        consumer_id (str): The consumer ID
        data (AttachmentItem): Document attachment data

    Returns:
        The uploaded document result
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.UploadDocument.create(data=data)


def invoicing_get_custom(consumer_id: str, custom_path: str, params=None):
    """Get custom data

    Args:
        consumer_id (str): The consumer ID
        custom_path (str): Custom path for the request
        params: Optional request parameters

    Returns:
        Custom data response
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Custom.all(custom_path, params=params)


def invoicing_create_custom(consumer_id: str, custom_path: str, data, params=None):
    """Create custom data

    Args:
        consumer_id (str): The consumer ID
        custom_path (str): Custom path for the request
        data: Data to create
        params: Optional request parameters

    Returns:
        Created custom data response
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Custom.create(custom_path, data, params=params)


def invoicing_update_custom(consumer_id: str, custom_path: str, chift_id: str, data, params=None):
    """Update custom data

    Args:
        consumer_id (str): The consumer ID
        custom_path (str): Custom path for the request
        chift_id (str): Chift ID of the item to update
        data: Data to update
        params: Optional request parameters

    Returns:
        Updated custom data response
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Custom.update(custom_path, chift_id, data, params=params)


def invoicing_get_custom_item(consumer_id: str, custom_path: str, chift_id: str, params=None):
    """Get custom item

    Args:
        consumer_id (str): The consumer ID
        custom_path (str): Custom path for the request
        chift_id (str): Chift ID of the item to get
        params: Optional request parameters

    Returns:
        Custom item response
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.invoicing.Custom.get(custom_path, chift_id, params=params)


def payment_get_balances(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPageBalanceItemOut:
    """Returns a list of balances.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPageBalanceItemOut: Paginated list of payment balances
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.payment.Balance.all(params={"page": page, "size": size})


def payment_get_transaction(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    accounting_category: TransactionAccountingCategory | None = TransactionAccountingCategory.all,
    starting_from: str | None = None,
    balance_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ChiftPageTransactionItemOut:
    """Returns a list of transactions.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        accounting_category (TransactionAccountingCategory)
        starting_from (str): Start from specific transaction ID
        balance_id (str): Filter by specific balance ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format

    Returns:
        ChiftPageTransactionItemOut: Paginated list of transactions
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.payment.Transaction.all(
        params={
            "page": page,
            "size": size,
            "accounting_category": accounting_category,
            "starting_from": starting_from,
            "balance_id": balance_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )


def payment_get_payments(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ChiftPagePaymentItemOut:
    """Returns a list of payments.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format

    Returns:
        ChiftPagePaymentItemOut: Paginated list of payments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.payment.Payment.all(
        params={"page": page, "size": size, "date_from": date_from, "date_to": date_to}
    )


def payment_get_payment(consumer_id: str, payment_id: str) -> PaymentItemOut:
    """Returns a specific payment.

    Args:
        consumer_id (str): The consumer ID
        payment_id (str): Unique identifier of the payment

    Returns:
        PaymentItemOut: The requested payment
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.payment.Payment.get(payment_id)


def payment_get_refunds(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    payment_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ChiftPageRefundItemOut:
    """Returns a list of refunds.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        payment_id (str): Filter by specific payment ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format

    Returns:
        ChiftPageRefundItemOut: Paginated list of payment refunds
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.payment.Refund.all(
        params={
            "page": page,
            "size": size,
            "payment_id": payment_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )


def pms_get_payments_methods(
    consumer_id: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
) -> ChiftPagePMSPaymentMethods:
    """Returns the list of payment methods.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page
        location_id (str): Location filter

    Returns:
        ChiftPagePMSPaymentMethods: Paginated list of PMS payment methods
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.PaymentMethod.all(
        params={"page": page, "size": size, "location_id": location_id}
    )


def pms_get_payments(
    consumer_id: str,
    date_from: str,
    date_to: str,
    page: int | None = 1,
    size: int | None = 50,
) -> ChiftPagePMSPaymentItem:
    """Returns a list of payments.

    Args:
        consumer_id (str): The consumer ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePMSPaymentItem: Paginated list of PMS payments
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Payment.all(
        params={"page": page, "size": size, "date_from": date_from, "date_to": date_to}
    )


def pms_get_locations(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePMSLocationItem:
    """Returns a list of the locations.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePMSLocationItem: Paginated list of PMS locations
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Location.all(params={"page": page, "size": size})


def pms_get_orders(
    consumer_id: str,
    date_from: str,
    date_to: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
    state: PMSStates | None = PMSStates.consumed,
) -> ChiftPagePMSOrderItem:
    """Returns a list of the orders.

    Args:
        consumer_id (str): The consumer ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        page (int): Page number for pagination
        size (int): Number of items per page
        location_id (str): Location filter
        state (PMSStates): Filter by order state

    Returns:
        ChiftPagePMSOrderItem: Paginated list of PMS orders
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Order.all(
        params={
            "page": page,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "location_id": location_id,
            "state": state,
        }
    )


def pms_get_closure(consumer_id: str, date: str, location_id: str | None = None) -> PMSClosureItem:
    """Returns whether the closure was already done for a specific day or not.

    Args:
        consumer_id (str): The consumer ID
        date (str): Date to check closure status for
        location_id (str): Location filter

    Returns:
        PMSClosureItem: Closure status information
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Closure.get(date=date, params={"location_id": location_id})


def pms_get_accounting_categories(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePMSAccountingCategoryItem:
    """Returns a list of accounting categories.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePMSAccountingCategoryItem: Paginated list of PMS accounting categories
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.AccountingCategory.all(params={"page": page, "size": size})


def pms_get_invoices(
    consumer_id: str,
    date_from: str,
    date_to: str,
    page: int | None = 1,
    size: int | None = 50,
    location_id: str | None = None,
) -> ChiftPagePMSInvoiceFullItem:
    """Returns a list of the invoices.

    Args:
        consumer_id (str): The consumer ID
        date_from (str): Start date filter in YYYY-MM-DD format
        date_to (str): End date filter in YYYY-MM-DD format
        page (int): Page number for pagination
        size (int): Number of items per page
        location_id (str): Location filter

    Returns:
        ChiftPagePMSInvoiceFullItem: Paginated list of PMS invoices
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Invoice.all(
        params={
            "page": page,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "location_id": location_id,
        }
    )


def pms_get_customers(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePMSCustomerItem:
    """Returns a list of all the customers.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePMSCustomerItem: Paginated list of PMS customers
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Customer.all(params={"page": page, "size": size})


def pms_get_customer(consumer_id: str, customer_id: str) -> PMSCustomerItem:
    """Returns a specific customer.

    Args:
        consumer_id (str): The consumer ID
        customer_id (str): Unique identifier of the customer

    Returns:
        PMSCustomerItem: The requested customer
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Customer.get(customer_id)


def pms_get_taxes(
    consumer_id: str, page: int | None = 1, size: int | None = 50
) -> ChiftPagePMSTaxRateItem:
    """Returns a list of the tax rates.

    Args:
        consumer_id (str): The consumer ID
        page (int): Page number for pagination
        size (int): Number of items per page

    Returns:
        ChiftPagePMSTaxRateItem: Paginated list of PMS tax rates
    """
    consumer = chift.Consumer.get(chift_id=consumer_id)
    return consumer.pms.Tax.all(params={"page": page, "size": size})
