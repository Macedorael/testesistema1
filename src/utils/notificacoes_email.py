import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from src.models.consulta import Appointment, Session
from src.models.paciente import Patient
from src.models.usuario import User
from urllib.parse import quote

def is_email_enabled():
    """
    Verifica se o envio de emails está habilitado
    
    Returns:
        bool: True se emails estão habilitados, False caso contrário
    """
    email_enabled = os.getenv('EMAIL_ENABLED', 'true').lower()
    return email_enabled in ['true', '1', 'yes', 'on']

def resolve_base_url() -> str:
    """Resolve a URL base pública para construir links em emails.
    Prioriza variável de ambiente explícita e faz fallback para URLs comuns
    de provedores ou para o contexto de requisição quando disponível.
    """
    # 1) Preferir BASE_URL explícita
    base = os.getenv('BASE_URL')
    if base:
        return base.rstrip('/')

    # 2) Fallbacks comuns de plataformas
    for env_name in (
        'RENDER_EXTERNAL_URL', 'RAILWAY_PUBLIC_DOMAIN', 'VERCEL_URL',
        'DEPLOY_URL', 'APP_URL', 'PUBLIC_URL'
    ):
        val = os.getenv(env_name)
        if val:
            if val.startswith('http://') or val.startswith('https://'):
                base = val
            else:
                base = f"https://{val}"
            return base.rstrip('/')

    # 3) Tentar contexto da requisição (se existir)
    try:
        from flask import request
        url_root = getattr(request, 'url_root', None)
        if url_root:
            return url_root.rstrip('/')
    except Exception:
        pass

    # 4) Último fallback: localhost conforme configuração
    host = os.getenv('HOST', 'localhost')
    port = os.getenv('PORT', '5000')
    scheme = os.getenv('URL_SCHEME', 'http')
    return f"{scheme}://{host}:{port}".rstrip('/')

def enviar_email_verificacao(email: str, username: str, token: str) -> bool:
    """
    Envia email de verificação de conta com link para confirmação.

    Args:
        email (str): Email do destinatário
        username (str): Nome de usuário
        token (str): Token de verificação

    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """

    # Verificar se envio está habilitado
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Email de verificação não será enviado.")
        return True

    try:
        # Configurações SMTP
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')

        # URL base para construir o link de verificação (robusto em produção)
        base_url = resolve_base_url()
        verify_link = f"{base_url}/api/verify-email?token={token}"

        if not sender_email or not sender_password:
            print("[ERROR] Configurações de email não encontradas no .env")
            return False

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Verifique seu email - Sistema Consultório"

        html_body = f"""
        <html>
        <body>
            <h2>Confirmação de Email</h2>
            <p>Olá {username},</p>
            <p>Obrigado por se cadastrar. Para concluir o processo, confirme seu email clicando no botão abaixo:</p>
            <p>
                <a href="{verify_link}" target="_blank" rel="noopener noreferrer" 
                   style="background-color: #4CAF50; color: white; padding: 10px 16px; text-decoration: none; border-radius: 4px;">
                    Confirmar meu email
                </a>
            </p>
            <p>Se você não solicitou este cadastro, ignore esta mensagem.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        print(f"[DEBUG] Email de verificação enviado para {email}")
        return True
    except Exception as e:
        print(f"[ERROR] Erro ao enviar email de verificação: {e}")
        return False

def gerar_link_google_calendar(titulo, data_inicio, data_fim=None, descricao="", local=""):
    """Gera um link para adicionar evento ao Google Calendar"""
    from datetime import timedelta
    
    if data_fim is None:
        data_fim = data_inicio + timedelta(hours=1)
    
    # Formatar datas no formato do Google Calendar (YYYYMMDDTHHMMSSZ)
    data_inicio_str = data_inicio.strftime('%Y%m%dT%H%M%S')
    data_fim_str = data_fim.strftime('%Y%m%dT%H%M%S')
    
    # Construir a URL do Google Calendar
    url_base = "https://calendar.google.com/calendar/render"
    params = {
        'action': 'TEMPLATE',
        'text': titulo,
        'dates': f"{data_inicio_str}/{data_fim_str}",
        'details': descricao,
        'location': local
    }
    
    query_string = '&'.join([f"{k}={quote(str(v))}" for k, v in params.items() if v])
    return f"{url_base}?{query_string}"

def enviar_email_confirmacao_agendamento(id_agendamento):
    """
    Envia email de confirmação de agendamento com links para Google Calendar
    
    Args:
        id_agendamento (int): ID do agendamento criado
    
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    
    # Verificar se emails estão habilitados
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Email de confirmação não será enviado.")
        return True  # Retorna True para não quebrar o fluxo da aplicação
    
    try:
        # Buscar informações do agendamento
        agendamento = Appointment.query.get(id_agendamento)
        if not agendamento:
            print(f"Agendamento com ID {id_agendamento} não encontrado")
            return False
        
        # Buscar informações do paciente
        paciente = Patient.query.get(agendamento.patient_id)
        if not paciente:
            print(f"Paciente não encontrado para o agendamento {id_agendamento}")
            return False
        
        # Buscar informações do funcionário (médico)
        from src.models.funcionario import Funcionario
        funcionario = None
        if agendamento.funcionario_id:
            funcionario = Funcionario.query.get(agendamento.funcionario_id)
        
        if funcionario:
            nome_doutor = f"Dr(a). {funcionario.nome}"
        else:
            # Fallback para o usuário se não houver funcionário
            usuario = User.query.get(agendamento.user_id)
            if usuario and usuario.email:
                nome_parte = usuario.email.split('@')[0]
                nome_doutor = f"Dr. {nome_parte.replace('.', ' ').title()}"
            else:
                nome_doutor = "Dr. Médico"
        
        # Usar a função global gerar_link_google_calendar
        
        # Buscar sessões do agendamento
        sessoes = Session.query.filter_by(appointment_id=id_agendamento).order_by(Session.data_sessao).all()
        
        # Gerar links individuais para cada sessão
        links_calendar = []
        for i, sessao in enumerate(sessoes, 1):
            titulo = f"Sessão Médica - {paciente.nome_completo}"
            descricao = f"Sessão {i} de {agendamento.quantidade_sessoes} com {nome_doutor}"
            link = gerar_link_google_calendar(
                titulo=titulo,
                data_inicio=sessao.data_sessao,
                descricao=descricao,
                local="Consultório"
            )
            
            links_calendar.append({
                'numero_sessao': i,
                'data_formatada': sessao.data_sessao.strftime('%d/%m/%Y às %H:%M'),
                'link_google_calendar': link
            })
        
        # Link para adicionar todas as sessões (primeira sessão como exemplo)
        if sessoes:
            titulo_todas = f"Sessões Médicas - {paciente.nome_completo}"
            descricao_todas = f"Série de {agendamento.quantidade_sessoes} sessões com {nome_doutor}"
            link_todas_sessoes = gerar_link_google_calendar(
                titulo=titulo_todas,
                data_inicio=sessoes[0].data_sessao,
                descricao=descricao_todas,
                local="Consultório"
            )
        else:
            link_todas_sessoes = "#"
        
        # Configurações de email do .env
        servidor_smtp = os.getenv('SMTP_SERVER')
        porta_smtp = int(os.getenv('SMTP_PORT', 587))
        email_remetente = os.getenv('SMTP_EMAIL')
        senha_email = os.getenv('SMTP_PASSWORD')
        
        if not all([servidor_smtp, email_remetente, senha_email]):
            print("Configurações de email não encontradas no arquivo .env")
            return False
        
        # Criar mensagem de email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = paciente.email
        msg['Subject'] = f"Confirmação de Agendamento - {paciente.nome_completo}"
        
        # Construir corpo do email em HTML
        frequencia_texto = {
            'semanal': 'semanal',
            'quinzenal': 'quinzenal', 
            'mensal': 'mensal'
        }.get(agendamento.frequencia, agendamento.frequencia)
        
        # Lista de sessões para o email
        lista_sessoes = ""
        for link_info in links_calendar:
            lista_sessoes += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{link_info['numero_sessao']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{link_info['data_formatada']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <a href="{link_info['link_google_calendar']}" 
                       style="background-color: #4285f4; color: white; padding: 8px 16px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Adicionar ao Google Calendar
                    </a>
                </td>
            </tr>
            """
        
        corpo_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Confirmação de Agendamento
                </h2>
                
                <p>Olá <strong>{paciente.nome_completo}</strong>,</p>
                
                <p>Seu agendamento foi confirmado com sucesso! Seguem os detalhes:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Detalhes do Agendamento</h3>
                    <p><strong>Médico:</strong> {nome_doutor}</p>
                    <p><strong>Primeira sessão:</strong> {agendamento.data_primeira_sessao.strftime('%d/%m/%Y às %H:%M')}</p>
                    <p><strong>Quantidade de sessões:</strong> {agendamento.quantidade_sessoes}</p>
                    <p><strong>Valor por sessão:</strong> R$ {float(agendamento.valor_por_sessao):.2f}</p>
                    <p><strong>Valor total:</strong> R$ {float(agendamento.valor_por_sessao * agendamento.quantidade_sessoes):.2f}</p>
                </div>
                
                <h3 style="color: #2c3e50;">Suas Sessões Agendadas</h3>
          
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #3498db; color: white;">
                            <th style="padding: 12px; border: 1px solid #ddd;">Sessão</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Data e Hora</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Google Calendar</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lista_sessoes}
                    </tbody>
                </table>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #27ae60;">💡 Dica:</h4>
                    <p>Recomendamos adicionar todas as sessões ao seu calendário para não esquecer dos compromissos!</p>
                </div>
                
                <p>Em caso de dúvidas ou necessidade de reagendamento, entre em contato conosco.</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe do Consultório</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Anexar corpo HTML
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_email)
            servidor.send_message(msg)
        
        print(f"Email de confirmação enviado com sucesso para {paciente.email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email de confirmação: {str(e)}")
        return False

def enviar_lembrete_sessao(id_sessao):
    """
    Envia lembrete por email para uma sessão específica
    
    Args:
        id_sessao (int): ID da sessão
    
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    
    # Verificar se emails estão habilitados
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Lembrete de sessão não será enviado.")
        return True  # Retorna True para não quebrar o fluxo da aplicação
    
    try:
        # Buscar informações da sessão
        sessao = Session.query.get(id_sessao)
        if not sessao:
            print(f"Sessão com ID {id_sessao} não encontrada")
            return False
        
        # Buscar agendamento relacionado
        agendamento = Appointment.query.get(sessao.appointment_id)
        if not agendamento:
            print(f"Agendamento não encontrado para a sessão {id_sessao}")
            return False
        
        # Buscar informações do paciente
        paciente = Patient.query.get(agendamento.patient_id)
        if not paciente:
            print(f"Paciente não encontrado para a sessão {id_sessao}")
            return False
        
        # Buscar informações do funcionário (médico)
        from src.models.funcionario import Funcionario
        funcionario = None
        if agendamento.funcionario_id:
            funcionario = Funcionario.query.get(agendamento.funcionario_id)
        
        if funcionario:
            nome_doutor = f"Dr(a). {funcionario.nome}"
        else:
            # Fallback para o usuário se não houver funcionário
            usuario = User.query.get(agendamento.user_id)
            if usuario and usuario.email:
                nome_parte = usuario.email.split('@')[0]
                nome_doutor = f"Dr. {nome_parte.replace('.', ' ').title()}"
            else:
                nome_doutor = "Dr. Médico"
        
        # Configurações de email do .env
        servidor_smtp = os.getenv('SMTP_SERVER')
        porta_smtp = int(os.getenv('SMTP_PORT', 587))
        email_remetente = os.getenv('SMTP_EMAIL')
        senha_email = os.getenv('SMTP_PASSWORD')
        
        if not all([servidor_smtp, email_remetente, senha_email]):
            print("Configurações de email não encontradas no arquivo .env")
            return False
        
        # Criar mensagem de email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = paciente.email
        msg['Subject'] = f"Lembrete: Consulta agendada para {sessao.data_sessao.strftime('%d/%m/%Y')}"
        
        # Usar a função global gerar_link_google_calendar
        
        titulo = f"Sessão Médica - {paciente.nome_completo}"
        descricao = f"Sessão {sessao.numero_sessao} de {agendamento.quantidade_sessoes} com {nome_doutor}"
        link_calendar = gerar_link_google_calendar(
            titulo=titulo,
            data_inicio=sessao.data_sessao,
            descricao=descricao,
            local="Consultório"
        )
        
        # Construir corpo do email em HTML
        corpo_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #f39c12; padding-bottom: 10px;">
                    🔔 Lembrete de Consulta
                </h2>
                
                <p>Olá <strong>{paciente.nome_completo}</strong>,</p>
                
                <p>Este é um lembrete da sua consulta agendada:</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f39c12;">
                    <h3 style="margin-top: 0; color: #856404;">Detalhes da Consulta</h3>
                    <p><strong>Data e Hora:</strong> {sessao.data_sessao.strftime('%d/%m/%Y às %H:%M')}</p>
                    <p><strong>Médico:</strong> {nome_doutor}</p>
                    <p><strong>Sessão:</strong> {sessao.numero_sessao} de {agendamento.quantidade_sessoes}</p>
                    <p><strong>Valor:</strong> R$ {float(sessao.valor):.2f}</p>
                    <p><strong>Local:</strong> Consultório</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link_calendar}" 
                       style="background-color: #4285f4; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        📅 Adicionar ao Google Calendar
                    </a>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #0c5460;">ℹ️ Informações Importantes:</h4>
                    <ul>
                        <li>Chegue com 10 minutos de antecedência</li>
                        <li>Traga um documento de identificação</li>
                        <li>Em caso de imprevisto, entre em contato conosco</li>
                    </ul>
                </div>
                
                <p>Aguardamos você!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe do Consultório</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Anexar corpo HTML
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_email)
            servidor.send_message(msg)
        
        print(f"Lembrete de sessão enviado com sucesso para {paciente.email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar lembrete de sessão: {str(e)}")
        return False

def enviar_email_atualizacao_agendamento(id_agendamento):
    """
    Envia email de notificação sobre atualização de agendamento
    
    Args:
        id_agendamento (int): ID do agendamento atualizado
    
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    
    # Verificar se emails estão habilitados
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Email de atualização não será enviado.")
        return True  # Retorna True para não quebrar o fluxo da aplicação
    
    try:
        # Buscar informações do agendamento
        agendamento = Appointment.query.get(id_agendamento)
        if not agendamento:
            print(f"Agendamento com ID {id_agendamento} não encontrado")
            return False
        
        # Buscar informações do paciente
        paciente = Patient.query.get(agendamento.patient_id)
        if not paciente:
            print(f"Paciente não encontrado para o agendamento {id_agendamento}")
            return False
        
        # Buscar informações do funcionário (médico)
        from src.models.funcionario import Funcionario
        funcionario = None
        if agendamento.funcionario_id:
            funcionario = Funcionario.query.get(agendamento.funcionario_id)
        
        if funcionario:
            nome_doutor = f"Dr(a). {funcionario.nome}"
        else:
            # Fallback para o usuário se não houver funcionário
            usuario = User.query.get(agendamento.user_id)
            if usuario and usuario.email:
                nome_parte = usuario.email.split('@')[0]
                nome_doutor = f"Dr. {nome_parte.replace('.', ' ').title()}"
            else:
                nome_doutor = "Dr. Médico"
        
        # Configurações de email do .env
        servidor_smtp = os.getenv('SMTP_SERVER')
        porta_smtp = int(os.getenv('SMTP_PORT', 587))
        email_remetente = os.getenv('SMTP_EMAIL')
        senha_email = os.getenv('SMTP_PASSWORD')
        
        if not all([servidor_smtp, email_remetente, senha_email]):
            print("Configurações de email não encontradas no arquivo .env")
            return False
        
        # Criar mensagem de email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = paciente.email
        msg['Subject'] = f"Agendamento Atualizado - {paciente.nome_completo}"
        
        # Buscar sessões do agendamento
        sessoes = Session.query.filter_by(appointment_id=id_agendamento).order_by(Session.data_sessao).all()
        
        # Gerar links individuais para cada sessão
        links_calendar = []
        for i, sessao in enumerate(sessoes, 1):
            titulo = f"Sessão Médica - {paciente.nome_completo}"
            descricao = f"Sessão {i} de {agendamento.quantidade_sessoes} com {nome_doutor}"
            link = gerar_link_google_calendar(
                titulo=titulo,
                data_inicio=sessao.data_sessao,
                descricao=descricao,
                local="Consultório"
            )
            
            links_calendar.append({
                'numero_sessao': i,
                'data_formatada': sessao.data_sessao.strftime('%d/%m/%Y às %H:%M'),
                'link_google_calendar': link
            })
        
        # Construir corpo do email
        frequencia_texto = {
            'semanal': 'semanal',
            'quinzenal': 'quinzenal', 
            'mensal': 'mensal'
        }.get(agendamento.frequencia, agendamento.frequencia)
        
        # Lista de sessões para o email
        lista_sessoes = ""
        for link_info in links_calendar:
            lista_sessoes += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{link_info['numero_sessao']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{link_info['data_formatada']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <a href="{link_info['link_google_calendar']}" 
                       style="background-color: #4285f4; color: white; padding: 8px 16px; 
                              text-decoration: none; border-radius: 3px; font-size: 12px;">
                        📅 Adicionar
                    </a>
                </td>
            </tr>
            """
        
        corpo_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #e67e22; padding-bottom: 10px;">
                    🔄 Agendamento Atualizado
                </h2>
                
                <p>Olá <strong>{paciente.nome_completo}</strong>,</p>
                
                <p>Seu agendamento foi atualizado com sucesso! Confira os novos detalhes:</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #e67e22;">
                    <h3 style="margin-top: 0; color: #856404;">📋 Detalhes Atualizados</h3>
                    <p><strong>Médico:</strong> {nome_doutor}</p>
                    <p><strong>Primeira Sessão:</strong> {agendamento.data_primeira_sessao.strftime('%d/%m/%Y às %H:%M')}</p>
                    <p><strong>Frequência:</strong> {frequencia_texto.title()}</p>
                    <p><strong>Quantidade de Sessões:</strong> {agendamento.quantidade_sessoes}</p>
                    <p><strong>Valor por Sessão:</strong> R$ {float(agendamento.valor_por_sessao):.2f}</p>
                    <p><strong>Valor Total:</strong> R$ {float(agendamento.quantidade_sessoes * agendamento.valor_por_sessao):.2f}</p>
                    {f'<p><strong>Observações:</strong> {agendamento.observacoes}</p>' if agendamento.observacoes else ''}
                </div>
                
                <h3 style="color: #2c3e50;">📅 Cronograma de Sessões Atualizado</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 12px; border: 1px solid #ddd;">Sessão</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Data/Hora</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Google Calendar</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lista_sessoes}
                    </tbody>
                </table>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #0c5460;">ℹ️ Importante:</h4>
                    <p>Por favor, atualize seu calendário com as novas datas e horários. Recomendamos adicionar todas as sessões ao Google Calendar.</p>
                </div>
                
                <p>Em caso de dúvidas sobre as alterações, entre em contato conosco.</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe do Consultório</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Anexar corpo HTML
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_email)
            servidor.send_message(msg)
        
        print(f"Email de atualização enviado com sucesso para {paciente.email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email de atualização: {str(e)}")
        return False

def enviar_email_cancelamento_agendamento(agendamento_data):
    """
    Envia email de notificação sobre cancelamento/exclusão de agendamento
    
    Args:
        agendamento_data (dict): Dados do agendamento que foi excluído
    
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    
    # Verificar se emails estão habilitados
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Email de cancelamento não será enviado.")
        return True  # Retorna True para não quebrar o fluxo da aplicação
    
    try:
        # Configurações de email do .env
        servidor_smtp = os.getenv('SMTP_SERVER')
        porta_smtp = int(os.getenv('SMTP_PORT', 587))
        email_remetente = os.getenv('SMTP_EMAIL')
        senha_email = os.getenv('SMTP_PASSWORD')
        
        if not all([servidor_smtp, email_remetente, senha_email]):
            print("Configurações de email não encontradas no arquivo .env")
            return False
        
        # Criar mensagem de email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = agendamento_data['patient_email']
        msg['Subject'] = f"Agendamento Cancelado - {agendamento_data['patient_name']}"
        
        corpo_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">
                    ❌ Agendamento Cancelado
                </h2>
                
                <p>Olá <strong>{agendamento_data['patient_name']}</strong>,</p>
                
                <p>Informamos que seu agendamento foi cancelado conforme solicitado.</p>
                
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #e74c3c;">
                    <h3 style="margin-top: 0; color: #721c24;">📋 Detalhes do Agendamento Cancelado</h3>
                    <p><strong>Médico:</strong> {agendamento_data['doctor_name']}</p>
                    <p><strong>Primeira Sessão:</strong> {agendamento_data['first_session_date']}</p>
                    <p><strong>Quantidade de Sessões:</strong> {agendamento_data['total_sessions']}</p>
                    <p><strong>Frequência:</strong> {agendamento_data['frequency']}</p>
                    <p><strong>Data do Cancelamento:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #0c5460;">ℹ️ Próximos Passos:</h4>
                    <ul>
                        <li>Remova as sessões do seu calendário pessoal</li>
                        <li>Entre em contato conosco se desejar reagendar</li>
                        <li>Caso tenha dúvidas sobre reembolsos, fale conosco</li>
                    </ul>
                </div>
                
                <p>Esperamos poder atendê-lo novamente em breve!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe do Consultório</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Anexar corpo HTML
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_email)
            servidor.send_message(msg)
        
        print(f"Email de cancelamento enviado com sucesso para {agendamento_data['patient_email']}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email de cancelamento: {str(e)}")
        return False

def enviar_email_reagendamento_sessao(id_sessao):
    """
    Envia email de notificação sobre reagendamento de sessão
    
    Args:
        id_sessao (int): ID da sessão reagendada
    
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    
    # Verificar se emails estão habilitados
    if not is_email_enabled():
        print("[INFO] Envio de emails desabilitado. Email de reagendamento não será enviado.")
        return True  # Retorna True para não quebrar o fluxo da aplicação
    
    try:
        # Buscar informações da sessão
        sessao = Session.query.get(id_sessao)
        if not sessao:
            print(f"Sessão com ID {id_sessao} não encontrada")
            return False
        
        # Buscar agendamento relacionado
        agendamento = Appointment.query.get(sessao.appointment_id)
        if not agendamento:
            print(f"Agendamento não encontrado para a sessão {id_sessao}")
            return False
        
        # Buscar informações do paciente
        paciente = Patient.query.get(agendamento.patient_id)
        if not paciente:
            print(f"Paciente não encontrado para a sessão {id_sessao}")
            return False
        
        # Buscar informações do funcionário (médico)
        from src.models.funcionario import Funcionario
        funcionario = None
        if agendamento.funcionario_id:
            funcionario = Funcionario.query.get(agendamento.funcionario_id)
        
        if funcionario:
            nome_doutor = f"Dr(a). {funcionario.nome}"
        else:
            # Fallback para o usuário se não houver funcionário
            usuario = User.query.get(agendamento.user_id)
            nome_doutor = "Dr(a). Responsável pelo Atendimento" if usuario else "Médico"
        
        # Configurações de email do .env
        servidor_smtp = os.getenv('SMTP_SERVER')
        porta_smtp = int(os.getenv('SMTP_PORT', 587))
        email_remetente = os.getenv('SMTP_EMAIL')
        senha_email = os.getenv('SMTP_PASSWORD')
        
        if not all([servidor_smtp, email_remetente, senha_email]):
            print("Configurações de email não encontradas no arquivo .env")
            return False
        
        # Criar mensagem de email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = paciente.email
        msg['Subject'] = f"Sessão Reagendada - {paciente.nome_completo}"
        
        # Gerar link para Google Calendar da nova sessão
        titulo = f"Sessão Médica - {paciente.nome_completo}"
        descricao = f"Sessão {sessao.numero_sessao} de {agendamento.quantidade_sessoes} com {nome_doutor}"
        link_google_calendar = gerar_link_google_calendar(
            titulo=titulo,
            data_inicio=sessao.data_sessao,
            descricao=descricao,
            local="Consultório"
        )
        
        # Formatação das datas
        data_original_formatada = sessao.data_original.strftime('%d/%m/%Y às %H:%M') if sessao.data_original else 'N/A'
        nova_data_formatada = sessao.data_sessao.strftime('%d/%m/%Y às %H:%M')
        
        corpo_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #f39c12; padding-bottom: 10px;">
                    🔄 Sessão Reagendada
                </h2>
                
                <p>Olá <strong>{paciente.nome_completo}</strong>,</p>
                
                <p>Sua sessão foi reagendada com sucesso! Confira os novos detalhes:</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f39c12;">
                    <h3 style="margin-top: 0; color: #856404;">📋 Detalhes do Reagendamento</h3>
                    <p><strong>Médico:</strong> {nome_doutor}</p>
                    <p><strong>Sessão:</strong> {sessao.numero_sessao} de {agendamento.quantidade_sessoes}</p>
                    <p><strong>Data Original:</strong> {data_original_formatada}</p>
                    <p><strong>Nova Data/Hora:</strong> {nova_data_formatada}</p>
                    {f'<p><strong>Observações:</strong> {sessao.observacoes_reagendamento}</p>' if hasattr(sessao, 'observacoes_reagendamento') and sessao.observacoes_reagendamento else ''}
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{link_google_calendar}" 
                       style="background-color: #4285f4; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 8px; display: inline-block;
                              font-size: 16px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        📅 Adicionar Nova Data ao Google Calendar
                    </a>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #0c5460;">ℹ️ Importante:</h4>
                    <ul>
                        <li>Remova a data anterior do seu calendário pessoal</li>
                        <li>Adicione a nova data clicando no botão acima</li>
                        <li>Anote a nova data e horário para não esquecer</li>
                    </ul>
                </div>
                
                <p>Em caso de dúvidas sobre o reagendamento, entre em contato conosco.</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe do Consultório</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Anexar corpo HTML
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_email)
            servidor.send_message(msg)
        
        print(f"Email de reagendamento enviado com sucesso para {paciente.email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email de reagendamento: {str(e)}")
        return False