import sys
from pyngrok import ngrok, conf

def configurar_ngrok():
    print("==" * 30)
    print("Configuração do Ngrok para hospedagem do TechCare")
    print("==" * 30)
    print("\nPara usar o Ngrok, você precisa ter uma conta (gratuita) e um token de autenticação.")
    print("Se você ainda não tem uma conta:")
    print("1. Acesse: https://dashboard.ngrok.com/signup")
    print("2. Crie uma conta gratuita")
    print("3. Obtenha seu token em: https://dashboard.ngrok.com/get-started/your-authtoken\n")
    
    token = input("Cole seu token de autenticação aqui: ").strip()
    
    if not token:
        print("Token não fornecido. Configuração cancelada.")
        return False
    
    try:
        ngrok.set_auth_token(token)
        print("\n✅ Token configurado com sucesso!")
        print("\nAgora você pode compartilhar a aplicação usando:")
        print("   python run_with_ngrok.py")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao configurar o token: {str(e)}")
        return False

if __name__ == "__main__":
    configurar_ngrok() 