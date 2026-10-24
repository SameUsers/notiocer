from src.application.dto.email_attachment import EmailAttachment
from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage
from src.infra.exchange.exchange_email_sender import ExchangeEmailSender


def test_send_email_uses_recipient_and_attachment_without_connecting(mocker):
    account_factory = mocker.patch('src.infra.exchange.exchange_email_sender.Account')
    credentials_factory = mocker.patch(
        'src.infra.exchange.exchange_email_sender.Credentials'
    )
    message_factory = mocker.patch('src.infra.exchange.exchange_email_sender.Message')
    attachment_factory = mocker.patch(
        'src.infra.exchange.exchange_email_sender.FileAttachment'
    )
    sender = ExchangeEmailSender(
        username='sender@example.com',
        password='test-password',
        defult_text='Invoice report',
        default_subject='Unpaid invoices',
    )
    message = PreparedInvoiceMessage(
        recipient_email='recipient@example.com',
        invoices=[],
        attachment=EmailAttachment(
            filename='invoices.xlsx', content_type='application/test', content=b'xlsx'
        ),
    )

    assert sender.send_email(message) is None

    credentials_factory.assert_called_once_with(
        username='sender@example.com', password='test-password'
    )
    account_factory.assert_called_once()
    account_arguments = account_factory.call_args.kwargs
    assert account_arguments['primary_smtp_address'] == 'sender@example.com'
    assert account_arguments['credentials'] is credentials_factory.return_value
    message_arguments = message_factory.call_args.kwargs
    assert message_arguments['account'] is account_factory.return_value
    assert (
        message_arguments['to_recipients'][0].email_address == 'recipient@example.com'
    )
    attachment_factory.assert_called_once_with(
        name='invoices.xlsx', content=b'xlsx', content_type='application/test'
    )
    message_factory.return_value.attach.assert_called_once_with(
        attachment_factory.return_value
    )
    assert message_arguments['subject'] == 'Unpaid invoices'
    assert message_arguments['body'] == 'Invoice report'
    message_factory.return_value.send_and_save.assert_not_called()
