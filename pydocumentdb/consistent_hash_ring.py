﻿#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import pydocumentdb.partition as partition
from struct import *

class _ConsistentHashRing(object):
    """The ConsistentHashRing class implements a consistent hash ring using the 
    hash generator specified.
    """
    def __init__(self, collection_links, partitions_per_node, hash_generator):
        """
        :Parameters:
            - `collection_links`: list, the links of collections participating in partitioning.
            - `partitions_per_node`: int, the partitions per node
            - `hash_generator`: HashGenerator, the hash generator to be used for hashing algorithm.
        """
        if collection_links is None:
            raise ValueError("collection_links is None.")

        if partitions_per_node <= 0 :
            raise ValueError("The partitions per node must greater than 0.")

        if hash_generator is None:
            raise ValueError("hash_generator is None.")

        self.collection_links = collection_links
        self.hash_generator = hash_generator

        self.partitions = self._ConstructPartitions(self.collection_links, partitions_per_node)
        
    def GetCollectionNode(self, partition_key):
        """Gets the SelfLink/ID based link of the collection node that maps to the partition key
        based on the hashing algorithm used for finding the node in the ring.

        :Parameters:
            - `partition_key`: str, the partition key to be used for finding the node in the ring.

        :Returns:
            str, the name of the collection mapped to that partition.

        """
        if partition_key is None:
            raise ValueError("partition_key is None or empty.")

        partition_number = self._FindPartition(self._GetBytes(partition_key))
        return self.partitions[partition_number].GetNode()

    def _ConstructPartitions(self, collection_links, partitions_per_node):
        """Constructs the partitions in the consistent ring by assigning them to collection nodes
        using the hashing algorithm and then finally sorting the partitions based on the hash value.
        """
        collections_node_count = len(collection_links)
        partitions = [partition._Partition() for i in range(0, partitions_per_node * collections_node_count)]

        index = 0
        for collection_node in collection_links:
            hash_value = self.hash_generator.ComputeHash(self._GetBytes(collection_node))
            for i in range(0, partitions_per_node):
                partitions[index] = partition._Partition(hash_value, collection_node)
                index += 1
                hash_value = self.hash_generator.ComputeHash(hash_value)

        partitions.sort()
        return partitions

    def _FindPartition(self, key):
        """Finds the partition from the byte array representation of the partition key.
        """
        hash_value = self.hash_generator.ComputeHash(key)
        return self._LowerBoundSearch(self.partitions, hash_value)

    def _GetSerializedPartitionList(self):
        """Gets the serialized version of the ConsistentRing. 
        Added this helper for the test code.
        """
        partition_list = list()
        
        for part in self.partitions:
            partition_list.append((part.node, unpack("<L", part.hash_value)[0]))

        return partition_list

    @staticmethod
    def _GetBytes(partition_key):
        """Gets the bytes representing the value of the partition key.
        """
        if isinstance(partition_key, basestring):
            return bytearray(partition_key, encoding='utf-8')
        else:
            raise ValueError("Unsupported " + str(type(partition_key)) + " for partitionKey.")

    @staticmethod
    def _LowerBoundSearch(partitions, hash_value):
        """Searches the partition in the partition array using hashValue.
        """
        for i in range(0, len(partitions) - 1):
            if partitions[i].CompareTo(hash_value) <= 0 and partitions[i+1].CompareTo(hash_value) > 0:
                return i

        return len(partitions) - 1
