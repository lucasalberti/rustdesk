# RustDesk by Visual Software

Base: RustDesk **1.4.9**, commit `6c578292e8ebbbec708b76986ba8c4bc7c509747`.
Destino: `lucasalberti/rustdesk`, branch de trabalho `visual-software-1.4.9`.

## Estado da preparação

A identidade visual e o fluxo de compilação estão preparados no código local.
Os instaladores **ainda não foram compilados nem testados em dispositivos**.
O acesso ao GitHub nesta sessão não está autenticado; nada foi enviado ao fork.

Verificações locais concluídas:

- Seis testes da configuração de servidor, cobrindo ausência de secrets, chaves
  inválidas, IPv4/IPv6 e rejeição de endereços malformados ou com credenciais.
- Workflows conferidos com actionlint 1.7.12 (sem shellcheck/pyflakes).
- Dependências dos nove jobs, ausência de publicação automática e referências
  aos parâmetros validadas.
- PNG, ICO, ICNS, XML do Android e plist do Mac lidos e validados.
- Diff conferido quanto a erros de espaços.

## Identidade visual

A logo foi obtida de `https://visualsoftware.inf.br/assets/logo-visual-home-CpVe0D4R.webp`.
O SHA-256 coincide com `src/assets/logo-visual-home.webp` do projeto do site:
`3a7822e577119373aac5a031cd36710ed5335bba5a9f01b34bd07f299dccc525`.

Os ícones vieram do favicon fornecido pelo usuário. O ICO contém uma imagem de
256 x 256; o PNG original tem 64 x 64. A imagem de 256 x 256 foi convertida para os
tamanhos nativos. Os maiores tamanhos do Mac são ampliados, sem criar detalhe novo.
Os originais ficam em `branding/visual-software/originals/`.

- Logo e texto “RustDesk by Visual Software” na interface Flutter.
- Fundo branco atrás da logo para manter a leitura nos temas claro e escuro.
- Ícones de Windows, Linux, macOS e Android.
- Nome de exibição do Android, metadados Windows/MSI, CFBundleDisplayName do Mac
  e nome do atalho Linux personalizados.
- Identificadores, executáveis, caminhos de dados, serviços, URI e driver de
  impressão continuam com os nomes internos RustDesk para preservar a migração.
  Portanto alguns títulos internos ainda mostram “RustDesk”. A versão não é
  destinada a instalação lado a lado com o cliente original.
- Licença e créditos do upstream preservados.

## Servidor próprio

O usuário confirmou que `RENDEZVOUS_SERVER` e `RS_PUB_KEY` já existem nos secrets
do fork. Seus valores não foram lidos nesta sessão.

| Secret | Uso |
|---|---|
| `RENDEZVOUS_SERVER` | Obrigatório: host do hbbs, com porta opcional; sem `https://` |
| `RS_PUB_KEY` | Obrigatório: chave **pública** Ed25519 do servidor, base64 de 32 bytes |
| `RELAY_SERVER` | Opcional: host/porta do hbbr |
| `API_SERVER` | Opcional: URL HTTP(S), normalmente utilizada com Server Pro |

O fluxo valida os valores e gera `src/visual_software_server.rs` antes de compilar.
Esse arquivo não é versionado. Não contém senhas de acesso remoto nem chave privada.
A geração é feita no host antes do build Linux em contêiner, para que os valores
também entrem nessa compilação.

As configurações são padrões do aplicativo, não bloqueios: configurações de rede
salvas explicitamente pelo usuário têm prioridade. As opções de segurança,
senhas e permissões de acesso remoto não são alteradas.

A verificação automática de atualizações do upstream fica desativada **por padrão**
para evitar substituir este fork pelo instalador original. Ela continua sendo uma
opção editável pelo usuário. Atualizações deste fork devem ser distribuídas pela
Visual Software até haver um canal de atualização próprio.

## Compilação no GitHub Actions

Executar **Visual Software — Windows, Linux, macOS, Android** depois que o workflow
estiver disponível no fork. É um fluxo manual (`workflow_dispatch`). Um workflow
novo precisa estar presente na branch padrão para aparecer no seletor do GitHub.

O fluxo gera artefatos do Actions, com retenção de 14 dias; não cria releases nem
publica instaladores automaticamente.

| Plataforma | Alvos preparados |
|---|---|
| Windows | x64 e ARM64; EXE e MSI |
| Linux | x64 e ARM64; DEB, RPM e AppImage (e pacote Arch x64 herdado) |
| macOS | Apple Silicon e Intel; DMG |
| Android | ARM64, ARMv7, x86_64 e APK universal |

O workflow deriva das etapas oficiais da tag 1.4.9. Os workflows oficiais foram
preservados para comparação; **utilizar os dois workflows Visual Software**,
pois eles também geram a configuração de servidor requerida pelo código.
Não ativar os antigos workflows agendados sem adaptar essa etapa.

### Assinatura Android

O fluxo exige estes secrets para não distribuir APKs assinados com uma chave de
depuração temporária:

- `ANDROID_SIGNING_KEY` (keystore em base64)
- `ANDROID_ALIAS`
- `ANDROID_KEY_STORE_PASSWORD`
- `ANDROID_KEY_PASSWORD`

Reutilizar a chave da versão antiga é necessário para atualizar o aplicativo
existente com o mesmo identificador. A presença desses secrets ainda precisa ser
confirmada pela execução autenticada no GitHub.

### Assinatura macOS

Com `MACOS_P12_BASE64`, `MACOS_P12_PASSWORD`, `MACOS_CODESIGN_IDENTITY` e
`MACOS_NOTARIZE_JSON`, o fluxo usa as etapas upstream de assinatura Developer ID e
autenticação pela Apple. Certificados e credenciais ainda não foram verificados.

Sem Developer ID, o DMG é **apenas para teste**, com assinatura ad hoc e exceção de
validação de bibliotecas limitada a esse aplicativo. Isso evita o erro de assinatura
do Flutter encontrado no binário antigo, mas **não equivale a autenticação Apple**;
o Gatekeeper ainda pode pedir liberação. Nenhuma proteção global do Mac é alterada.

### Assinatura Windows

O fluxo mantém a integração opcional upstream com o serviço de assinatura
(`SIGN_BASE_URL`/`SIGN_SECRET_KEY`). Sem ela, EXE e MSI ficam sem assinatura de
editor. Essa integração ainda precisa ser validada com o serviço da empresa.

## Manutenção e validação pendente

Para regenerar os workflows após revisar alterações no upstream:

```sh
python3 -m pip install PyYAML==6.0.2
python3 tools/visual-software/generate_workflow.py
python3 -m unittest discover -s tools/visual-software -p 'test_*.py'
```

A compilação real deve confirmar a disponibilidade dos runners, dependências,
certificados e secrets. Depois, testar conexão direta e via relay ao servidor da
Visual, transferência de arquivos, permissões de tela/entrada, atualização sobre
o fork antigo e reinicialização. Nenhuma dessas verificações de funcionamento
foi substituída pelos testes de configuração locais.

Antes da distribuição, disponibilizar o código correspondente à compilação e
as informações necessárias para reproduzi-la, conforme a licença AGPL-3.0.

