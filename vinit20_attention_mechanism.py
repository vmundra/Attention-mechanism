# -*- coding: utf-8 -*-
"""vinit20- attention_mechanism

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tiHtoDkeoj1WwLXGGy3JeNjrjt8rWZbp
"""

from google.colab import drive
drive.mount('/content/drive')

import torch 
import torch.nn as nn

class EncoderLSTM(nn.Module):
  def __init__(self,input_size, hidden_size, n_layers = 1, drop_prob = 0):

    super(EncoderLSTM, self).__init__()
    self.hidden_size = hidden_size
    self.n_layers = n_layers

    self.embedding = nn.Embedding(input_size, hidden_size)  # iska matlab kya hota h? iska matlab ye h kya ki input ka size rahega input_size but fir next wala hidden_size ka matlab kya h?
                                                            # uska matlab kya hidden_size ka jitna size h utna Embedding layer me jane ka baad apne vector ka size hojayega???
    self.lstm = nn.LSTM(hidden_size, hidden_size, n_layers, dropout = drop_prob, batch_first = True)


  def forward(self,inputs,hidden):
    #Embed the inputs
    embedded = self.embedding(inputs)
    #Pass the embedded word vectors into LSTM and return all the outputs
    output, hidden = self.lstm(embedded, hidden)
    return output, hidden

  def init_hidden(self,batch_size =1):

    return (torch.zeros(self.n_layers, batch_size, self.hidden_size, device = device), ##WTF??????????????????
            torch.zeros(self.n_layers, batch_size, self.hidden_size, device = device))  ## ye kya kr rha h????????????????????????????????

class BahdanauDecoder(nn.Module):
  def __init__(self,hidden_size,output_size, n_layers= 1, drop_prob = 0.1):  ## abhi isme output_size ko kyu daala h parameters me??????
    super(BahdanauDecoder, self).__init__()

    self.hidden_size = hidden_size
    self.output_size = output_size
    self.n_layers = n_layers
    self.drop_prob = drop_prob

    self.embedding = nn.Embedding(self.output_size, self.hidden_size)

    self.fc_hidden = nn.Linear(self.hidden_size, self.hidden_size, bias = False) ##ok samjha ye apna feed forward ke liye hi h uska input ad output dimension
                                                                                 ## but ek doubt h Floydhub walo ke diagram me (https://blog.floydhub.com/attention-mechanism/) isme dhundh le
                                                                                 ## decoder_hidden ka size (n*1) dimension h 
                                                                                 ## and enocder_outputs ka size (n*n) h
                                                                                 ## ye humne yaha kaha define kiiya h
                                                                                 ## humne to dono fc_encoder (just neeche wala) and fc_hidden
                                                                                 ## dono ka input and output dimension same bhataya h

    self.fc_encoder = nn.Linear(self.hidden_size, self.hidden_size, bias = False)
    self.weight = nn.Parameter(torch.FloatTensor(1, hidden_size))  ## WTF is this now??
    self.attn_combine = nn.Linear(self.hidden_size * 2, hidden_size)
    self.dropout = nn.Dropout(self.drop_prob)
    self.lstm = nn.Linear(self.hidden_size * 2, self.hidden_size, batch_first=True) #is this self.hidden_size * 2 for the enocder's input
                                                                                    # i.e word_embedding * prev_hidden_state iske liye *2 kiya h na?

    self.classifier = nn.Linear(self.hidden_size, self.output_size) ## and ye bhi kya h bhai??


  def forward(self, inputs, hidden, encoder_outputs):

    encoder_outputs = encoder_outputs.squeeze()  # why squeezing????? maine neeche kiya h ek example wo dekh vinit variable ka naam h wo wala
                                                  # I guess uske liye hi kiya hoga
                                                  #taki agar say array ka size kuchh (1,1,1,2,3) h to squeeze se uska size (2,3) ho jata h and agar (1,1,2,3) h to bhi (2,3) ho jata h

    #Embed the inputs in decoder
    embedded = self.embedding(inputs).view(1,-1) # why .view(1,-1) over here?? enocder me to nhi kiya tha ye # itna pata h ki kyuki shayad isko
                                                 # decoder ke andar input (1*some_num) ye dim ka vector chahiye isliye kiys hoga
                                                 # but then encoder ke time kyu nhi kiya ???
                                                 #mera guess h ki shayad context vector ke sath multiply ktrna h isliye aisa kiya hoga, still confirm krna h
    embedded = self.dropout(embedded)

    #Calculating Alignment Scores
    #Alignment scores tere feedforward layers ke andar jakr jo output aata h wo h
    # matlab end me uska tanh hoga jaise feed forward neural nets me hota h




    #(samjha)=> ye fc_hidden[0] and encoder_outputs pass honge upar wale feedforward layers se (upar jo self.fc and aisa likha h usse)
    #I guess
    #lekin isme bas ye bhata ki ye say apne pass H_decoder and H_encoder h
    #but isko apan dekh tanh me mulitply krte h weights se
    #isko multiply kaha kiya h apan ne weights se??
    # x actually hoga kuchh aisa => tanh([n*1] * [weights ka dimension](jo dega (n*1)) + (n*2)*(weigths ka dimension)(jo dega (n*2))) and iska output hoga tanh krke=> (n*2) dimension
    #and isko apan neeche (1*n) ke sath multiply karenge to apan ko actually me (1*n) * (n*2) matalb (1*2) size ka vector milega
    # ye bhi doubt h ki encoder_outputs ka dimension hamesha n*(2) ye (2) hi hoga kya??
    x = torch.tanh(self.fc_hidden(hidden[0]) + self.fc_encoder(encoder_outputs)) # so ye samjha ki ye tanh actually feed forward ka last ka output ke liye krte h
                                                                                 # but isme ye do kyu pass kiya h self.fc_hidden(hidden[0]) + self.fc_encoder(encoder_outputs)
                                                                                 # self.fc_hidden(hidden[0]) ka matlab decoder ka hidden state kya????
                                                                                 # and agar ye wo h to kya decoder ke hidden_State ka and enocder ke output ka addition hota h kya attention mechanism ke sabse start me?????????


    #(samjha) => but bas itna bhata de ki ye unsqueeze 2 kyu??
    # yaha basicaaly formula jo ki ye h ....score = W_combined.tanh(W_decoder*H_decoder + W_encoder*H_encoder) krna h and tanh(something) wo pura apna x h
    alignment_scores = x.bmm(self.weight.unsqueeze(2)) # agar yaha unsqueeze kr rhe h I guess kyuki encoder_outputs ko pehle squeeze kiys tha
                                                       # but agar aisa h 
                                                       # to apan ne to upar x calcuate krte time
                                                       # hidden[0] ko to squeeze nhi kiya?
                                                       # coz agar usko krte to haa thik lagta ki unsqueeze kiya h
                                                       # to kya iska matlab hidden[0] ye [0] hi squeeze krleta h kya
                                                       # to fir encoder_outputs[0] krke try kr aar aisa h to 
                                                       # and aagar sab kucch samjha to fir ye bhata ki ye
                                                       # unsqueeze[2] ye [2] kyu kiya h?????????????????/


    #softmaxing the alignment scores to get the attention weights
    #attn_weights ka dimension (1*2) hoga
    attn_weights = F.softmax(alignment_scores.view(1,-1), dim=1) # and yaha view kyu kiya h? 

    ##################################################
    #main Doubt upar tak attn_weights ka dimension tha (1*2)
    #but yaha multiply krte time wo (2*1) banjata h aisa kyu???????????
    #I guess agar isko ulta krke matlab agar attn_weights ko pehle rakha and encoder ko attn_weights ke upar wale dimension ke sath multiply kiy ato same hi aayega to ye doubt clear h
    ##################################################
    #context_vector ka dimension hoga   =>  [encoder_outputs] i.e (n*2) mulitply with attn_weights (2*1) equals to= (1*n)
    #multiplying the attention weights with the enocder outputs to get the context vector
    context_vector = torch.bmm(attn_weights.unsqueeze(0),
                               encoder_outputs.unsqueeze(0))
    

    #Concatenating context vector with the embedded input of decoder
    #abhi yaha pr decoder ka input context_vector jisla dimension h (1*n) and decoder_input (1*n) ye add hoga and (1*n) banega
    output = torch.cat((embedded, context_vector[0]), 1).unsqueeze(0) #ye yaha torch.cat ke andar 2 brackets kyu h????
                                                                      #and firse unsqueeze(0) kyu jab mann chaha tab krte h kya bc

    
    #Passing the concatenated vector as input to the LSTM cell
    output, hidden = self.lstm(output, hidden)

    #Passing the LSTM output through a Linear layer acting as a classifier
    output = F.log_softmax(self.classifier(output[0]), dim=1) #WTF classifier upar initialize kiya h but ye naya kya aa gaya h abhi???

    #(samjha) shayad apan attn_weights isliye reutrn krte h kyuki backporopogation ke time unka weights update krna hota h
    return output, hidden, attn_weights  #ye attn_weights kyu return kr rha h tu bcccccccccccccccc????????

g = nn.Parameter(torch.FloatTensor(1,5))

g

h = torch.FloatTensor(1,5)
h

h = nn.Parameter(h)
h

"""#Squeeze ka eg:-"""

vinit = [[[[[1,2,3], [5,6,7]]]]]
import numpy as np
v = np.array(vinit)

v
v.shape

import numpy as np
vinit = np.squeeze(vinit)

vinit

vinit.shape

vinit = np.unsqueeze(0)(vinit)
vinit
vinit.shape

"""#Idhar tak squeeze"""

