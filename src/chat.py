from search import search_prompt

def main():
    print("Chat iniciado. Digite 'quit', 'exit' ou 'sair' para encerrar.")
    
    while True:
        try:
            question = input("\nFaça sua pergunta: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'sair']:
                print("Encerrando chat.")
                break
            
            response = search_prompt(question)
            print(f"\nRESPOSTA: {response}")
            
        except KeyboardInterrupt:
            print("\nEncerrando chat.")
            break
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}")

if __name__ == "__main__":
    main()