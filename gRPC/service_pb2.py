# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x08\x63hatroom\"\x18\n\x04User\x12\x10\n\x08username\x18\x01 \x01(\t\"E\n\x0b\x43hatMessage\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x13\n\x0btarget_name\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\"\x1c\n\x08Wildcard\x12\x10\n\x08wildcard\x18\x01 \x01(\t\"0\n\x0c\x46\x65tchRequest\x12\x0e\n\x06msg_id\x18\x01 \x01(\x05\x12\x10\n\x08username\x18\x02 \x01(\t\"D\n\x0fGeneralResponse\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t2\x9e\x03\n\x08\x43hatRoom\x12\x41\n\x12rpc_create_account\x12\x0e.chatroom.User\x1a\x19.chatroom.GeneralResponse\"\x00\x12@\n\x11rpc_check_account\x12\x0e.chatroom.User\x1a\x19.chatroom.GeneralResponse\"\x00\x12:\n\x10rpc_list_account\x12\x12.chatroom.Wildcard\x1a\x0e.chatroom.User\"\x00\x30\x01\x12\x41\n\x12rpc_delete_account\x12\x0e.chatroom.User\x1a\x19.chatroom.GeneralResponse\"\x00\x12\x46\n\x10rpc_send_message\x12\x15.chatroom.ChatMessage\x1a\x19.chatroom.GeneralResponse\"\x00\x12\x46\n\x11rpc_fetch_message\x12\x16.chatroom.FetchRequest\x1a\x15.chatroom.ChatMessage\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USER._serialized_start=27
  _USER._serialized_end=51
  _CHATMESSAGE._serialized_start=53
  _CHATMESSAGE._serialized_end=122
  _WILDCARD._serialized_start=124
  _WILDCARD._serialized_end=152
  _FETCHREQUEST._serialized_start=154
  _FETCHREQUEST._serialized_end=202
  _GENERALRESPONSE._serialized_start=204
  _GENERALRESPONSE._serialized_end=272
  _CHATROOM._serialized_start=275
  _CHATROOM._serialized_end=689
# @@protoc_insertion_point(module_scope)
