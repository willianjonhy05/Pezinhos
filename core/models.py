from django.db import models
from datetime import date
from django.contrib.auth import get_user_model
from django.utils import timezone

# Classe Usuario com associação ao modelo de usuário padrão
class Usuario(models.Model):
    nome = models.CharField('Nome', max_length=255)
    data_nasc = models.DateField('Data de Nascimento', null=True, blank=True)
    foto = models.ImageField("Foto", upload_to='avatares', blank=True, null=True)
    email = models.EmailField('E-mail')
    telefone = models.CharField("Telefone", max_length=15, null=True, blank=True)
    cpf = models.CharField("CPF", max_length=15, null=True, blank=True)
    user = models.OneToOneField(get_user_model(), verbose_name="Usuário", on_delete=models.CASCADE, null=True, blank=True, related_name="usuario")

    @property
    def idade(self):
        hoje = date.today()
        diferenca = hoje - self.data_nasc
        return round(diferenca.days // 365.25)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


# Classe ProfissionalDePodologia
class ProfissionalDePodologia(models.Model):
    nome = models.CharField(max_length=100)
    biografia = models.TextField(help_text="Descrição do profissional e sua experiência")
    especializacao = models.CharField(max_length=100, help_text="Especialização, como atendimento infantil, TEA/TDAH etc.")
    anos_de_experiencia = models.IntegerField(help_text="Anos de experiência do profissional")
    email_contato = models.EmailField(help_text="E-mail de contato do profissional")
    telefone_contato = models.CharField(max_length=15, null=True, blank=True, help_text="Telefone de contato")
    site = models.URLField(null=True, blank=True, help_text="Website ou página de contato do profissional")
    endereco_clinica = models.CharField(max_length=255, null=True, blank=True, help_text="Endereço da clínica onde atende")
    especialista_em_pediatria = models.BooleanField(default=True, help_text="Se o profissional é especializado no atendimento pediátrico")
    idiomas_suportados = models.JSONField(default=list, help_text="Idiomas suportados para comunicação, ex: ['Português', 'Libras']")
    servicos_oferecidos = models.ManyToManyField('ServicoDePodologia', related_name="profissionais", blank=True)

    class Meta:
        verbose_name = "Profissional de Podologia"
        verbose_name_plural = "Profissionais de Podologia"

    def __str__(self):
        return f"{self.nome} - {self.especializacao}"


# Classe ServicoDePodologia com relação a ProfissionalDePodologia
class ServicoDePodologia(models.Model):
    nome = models.CharField(max_length=100, help_text="Nome do serviço de podologia")
    descricao = models.TextField(help_text="Descrição detalhada do serviço")
    etapas_preparacao = models.TextField(help_text="Passo a passo de preparação para o serviço")
    instrucoes = models.TextField(help_text="Instruções para execução do serviço")
    imagem = models.ImageField(upload_to='servicos/', null=True, blank=True, help_text="Imagem ilustrativa do serviço")
    video = models.URLField(null=True, blank=True, help_text="URL para vídeo explicativo do serviço")

    class Meta:
        verbose_name = "Serviço de Podologia"
        verbose_name_plural = "Serviços de Podologia"

    def __str__(self):
        return self.nome


# Classe Artigo com relação a ProfissionalDePodologia e Usuario
class Artigo(models.Model):
    CATEGORIAS = [
        ('podologia', 'Podologia'),
        ('saude', 'Saúde Geral'),
        ('cuidado', 'Dicas de Cuidado'),
        ('acessibilidade', 'Acessibilidade'),
    ]
    
    titulo = models.CharField(max_length=150, help_text="Título do artigo")
    conteudo = models.TextField(help_text="Conteúdo completo do artigo")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, help_text="Categoria do artigo")
    autor = models.ForeignKey(ProfissionalDePodologia, on_delete=models.SET_NULL, null=True, blank=True, related_name="artigos", help_text="Autor do artigo")
    data_publicacao = models.DateField(auto_now_add=True, help_text="Data de publicação do artigo")
    imagem = models.ImageField(upload_to='artigos/', null=True, blank=True, help_text="Imagem ilustrativa do artigo")
    video = models.URLField(null=True, blank=True, help_text="URL para vídeo explicativo do artigo")
    audio = models.URLField(null=True, blank=True, help_text="URL para áudio explicativo do artigo")
    favoritado_por = models.ManyToManyField(Usuario, related_name="artigos_favoritos", blank=True)

    class Meta:
        verbose_name = "Artigo"
        verbose_name_plural = "Artigos"
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo


# Classe FaleConosco com relação a Usuario
class FaleConosco(models.Model):
    nome = models.CharField(max_length=100, help_text="Nome do remetente")
    email = models.EmailField(help_text="E-mail para contato")
    assunto = models.CharField(max_length=150, help_text="Assunto da mensagem")
    mensagem = models.TextField(help_text="Conteúdo da mensagem")
    data_envio = models.DateTimeField(auto_now_add=True, help_text="Data e hora do envio da mensagem")
    respondida = models.BooleanField(default=False, help_text="Indica se a mensagem já foi respondida")
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="mensagens", help_text="Usuário que enviou a mensagem")

    class Meta:
        verbose_name = "Fale Conosco"
        verbose_name_plural = "Fale Conosco"
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.nome} - {self.assunto}"


class ConfirmacaoDeAtendimento(models.Model):
    TIPOS_NOTIFICACAO = [
        ('app', 'Notificação no Aplicativo'),
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="confirmacoes",
        help_text="Usuário que agendou o atendimento"
    )
    profissional = models.ForeignKey(
        'ProfissionalDePodologia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmacoes",
        help_text="Profissional de podologia responsável pelo atendimento"
    )
    servico = models.ForeignKey(
        'ServicoDePodologia',
        on_delete=models.CASCADE,
        related_name="confirmacoes",
        help_text="Serviço de podologia agendado"
    )
    data_agendamento = models.DateTimeField(help_text="Data e hora do atendimento agendado")
    tipo_notificacao = models.CharField(
        max_length=10,
        choices=TIPOS_NOTIFICACAO,
        default='app',
        help_text="Método de notificação escolhido pelo usuário"
    )
    tempo_antecedencia = models.DurationField(
        help_text="Tempo antes do atendimento para enviar o lembrete (em horas ou dias)"
    )
    notificacao_enviada = models.BooleanField(
        default=False,
        help_text="Indica se a notificação já foi enviada"
    )

    def __str__(self):
        return f"Confirmação para {self.usuario} - {self.servico} com {self.profissional}"

    def enviar_notificacao(self):
        """
        Função para enviar notificação baseada no tipo de preferência do usuário.
        """
        if self.tipo_notificacao == 'app':
            # Lógica para enviar notificação no app
            pass
        elif self.tipo_notificacao == 'email':
            # Lógica para enviar e-mail de confirmação
            pass
        elif self.tipo_notificacao == 'whatsapp':
            # Lógica para enviar mensagem de WhatsApp
            pass
        self.notificacao_enviada = True
        self.save()

    def verificar_notificacao(self):
        """
        Verifica se está no momento correto para enviar a notificação.
        """
        momento_para_enviar = self.data_agendamento - self.tempo_antecedencia
        if timezone.now() >= momento_para_enviar and not self.notificacao_enviada:
            self.enviar_notificacao()

    class Meta:
        verbose_name = "Confirmação de Atendimento"
        verbose_name_plural = "Confirmações de Atendimento"
        ordering = ['-data_agendamento']