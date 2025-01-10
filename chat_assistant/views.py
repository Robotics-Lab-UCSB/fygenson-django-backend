from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import fasttext

# Load the models
GENERAL_MODEL_PATH = "./models/general_intent_model.bin"
OBJECT_MODEL_PATH = "./models/object_intent_model.bin"
general_model = fasttext.load_model(GENERAL_MODEL_PATH)
object_model = fasttext.load_model(OBJECT_MODEL_PATH)

@csrf_exempt
def predict_intentions(request):
    if request.method == 'POST':
        try:
            # Parse the input JSON
            body = json.loads(request.body)
            message = body.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Predict general intent
            general_label, general_confidence = general_model.predict(message)
            general_intent = general_label[0].replace('__label__', '')

            # Predict object intent
            object_label, object_confidence = object_model.predict(message)
            object_intent = object_label[0].replace('__label__', '')

            # Return both predictions
            return JsonResponse({
                'general_intention': general_intent,
                'general_confidence': f"{general_confidence[0]}",
                'object_intention': object_intent,
                'object_confidence': f"{object_confidence[0]}"
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
